function threeSum(nums: number[]): number[][] {
	const result: number[][] = [];
	const sortedNums = nums.sort((a, b) => a - b);

	for (let i = 0; i < sortedNums.length - 2; i++) {
		if (i > 0 && sortedNums[i] === sortedNums[i - 1]) {
			continue; // Skip duplicates
		}

		let left = i + 1;
		let right = sortedNums.length - 1;

		while (left < right) {
			const sum = sortedNums[i] + sortedNums[left] + sortedNums[right];

			if (sum === 0) {
				result.push([sortedNums[i], sortedNums[left], sortedNums[right]]);
				left++;
				right--;

				while (left < right && sortedNums[left] === sortedNums[left - 1]) {
					left++; // Skip duplicates
				}
				while (left < right && sortedNums[right] === sortedNums[right + 1]) {
					right--; // Skip duplicates
				}
			} else if (sum < 0) {
				left++;
			} else {
				right--;
			}
		}
	}

	return result;
}

// Example usage:
const nums = [-1, 0, 1, 2, -1, -4];
const result = threeSum(nums);
console.log(result);