def max_subarray_sum(nums):
    max_current = max_global = nums[0]
    start, best_start, best_end = 0, 0, 0

    for i in range(1, len(nums)):
        if nums[i] > max_current + nums[i]:
            max_current = nums[i]
            start = i
        else:
            max_current += nums[i]

        if max_current > max_global:
            max_global = max_current
            best_start, best_end = start, i

    return max_global, nums[best_start:best_end + 1]


if __name__ == "__main__":
    nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    total, subarray = max_subarray_sum(nums)
    print(f"Max sum: {total}, Subarray: {subarray}")
