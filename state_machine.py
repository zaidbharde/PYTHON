from dataclasses import dataclass, field
from typing import Callable, Optional
from datetime import datetime

@dataclass
class Transition:
    from_state: str
    to_state:   str
    event:      str
    guard:      Optional[Callable] = None
    action:     Optional[Callable] = None

class StateMachine:
    def __init__(self, name, initial_state):
        self.name        = name
        self.state       = initial_state
        self.transitions = []
        self.history     = [(initial_state, "init", datetime.now())]
        self.on_enter    = {}
        self.on_exit     = {}

    def add(self, from_state, event, to_state, guard=None, action=None):
        self.transitions.append(Transition(from_state, to_state, event, guard, action))
        return self

    def when_enter(self, state, callback):
        self.on_enter[state] = callback
        return self

    def when_exit(self, state, callback):
        self.on_exit[state] = callback
        return self

    def trigger(self, event, **ctx):
        for t in self.transitions:
            if t.from_state == self.state and t.event == event:
                if t.guard and not t.guard(ctx):
                    print(f"  ⚠️  Guard blocked: {event}")
                    return False

                old = self.state

                if old in self.on_exit:
                    self.on_exit[old](old, ctx)

                if t.action:
                    t.action(ctx)

                self.state = t.to_state
                self.history.append((t.to_state, event, datetime.now()))

                if t.to_state in self.on_enter:
                    self.on_enter[t.to_state](t.to_state, ctx)

                print(f"  {old} --[{event}]--> {self.state}")
                return True

        print(f"  ❌ No transition: {self.state} + {event}")
        return False

    def can(self, event):
        return any(t.from_state == self.state and t.event == event for t in self.transitions)

    def available_events(self):
        return [t.event for t in self.transitions if t.from_state == self.state]

    def print_history(self):
        print(f"\n  History ({self.name}):")
        for state, event, ts in self.history:
            print(f"    {ts.strftime('%H:%M:%S')} | {event:15} → {state}")


if __name__ == "__main__":
    print("=" * 50)
    print("  State Machine — Order Lifecycle")
    print("=" * 50)

    order = StateMachine("Order", "created")

    (order
        .add("created",    "pay",      "paid",       guard=lambda ctx: ctx.get("amount", 0) > 0)
        .add("paid",       "ship",     "shipped")
        .add("shipped",    "deliver",  "delivered")
        .add("delivered",  "return",   "returned")
        .add("created",    "cancel",   "cancelled")
        .add("paid",       "cancel",   "cancelled")
        .add("paid",       "refund",   "refunded")
        .add("returned",   "refund",   "refunded"))

    order.when_enter("paid",      lambda s, c: print(f"    💰 Payment received: ${c.get('amount', 0)}"))
    order.when_enter("shipped",   lambda s, c: print(f"    📦 Package shipped"))
    order.when_enter("delivered", lambda s, c: print(f"    ✅ Delivered"))
    order.when_enter("cancelled", lambda s, c: print(f"    🚫 Order cancelled"))

    print(f"\n  State: {order.state}")
    print(f"  Available: {order.available_events()}")

    order.trigger("pay", amount=0)
    order.trigger("pay", amount=49.99)
    order.trigger("ship")

    print(f"\n  Can cancel? {order.can('cancel')}")
    print(f"  Can deliver? {order.can('deliver')}")

    order.trigger("deliver")
    order.trigger("return")
    order.trigger("refund")

    order.print_history()

    print(f"\n{'=' * 50}")
    print("  State Machine — Traffic Light")
    print("=" * 50)

    light = StateMachine("TrafficLight", "red")
    (light
        .add("red",    "next", "green")
        .add("green",  "next", "yellow")
        .add("yellow", "next", "red")
        .add("red",    "emergency", "flashing")
        .add("green",  "emergency", "flashing")
        .add("yellow", "emergency", "flashing")
        .add("flashing", "reset", "red"))

    emojis = {"red": "🔴", "green": "🟢", "yellow": "🟡", "flashing": "⚡"}
    light.when_enter("red",    lambda s, c: print(f"    {emojis[s]} STOP"))
    light.when_enter("green",  lambda s, c: print(f"    {emojis[s]} GO"))
    light.when_enter("yellow", lambda s, c: print(f"    {emojis[s]} CAUTION"))

    for _ in range(6):
        light.trigger("next")

    light.trigger("emergency")
    light.trigger("reset")
    light.print_history()
