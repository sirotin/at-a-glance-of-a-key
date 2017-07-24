#pragma once

#include <numeric>
#include <iostream>
#include <algorithm>
#include <forward_list>

struct Counter
{
	Counter()
		: m_min(-1)
		, m_max(0)
		, m_acc(0)
		, m_num(0)
	{
	}

	void submit(uint64_t value)
	{
		m_min = std::min(m_min, value);
		m_max = std::max(m_max, value);

		m_acc += value;
		++m_num;

		m_numbers.emplace_front(value);
	}

	uint64_t min() const { return (m_num > 0) ? m_min : 0; }
	uint64_t max() const { return (m_num > 0) ? m_max : 0; }
	double avg() const { return (m_num > 0) ? static_cast<double>(m_acc) / m_num : 0; }
	double stdev() const
	{
		if (m_num == 0) {
			return 0;
		}

		double sq_sum = std::inner_product(m_numbers.begin(), m_numbers.end(), m_numbers.begin(), 0.0);
		double mean = avg();
		return std::sqrt(sq_sum / m_num - mean * mean);
	}

	void dump(const std::string& name) const
	{
		std::cout << name << ": min=" << m_min << ", max=" << m_max << ", mean=" << avg() << ", stddev=" << stdev() << std::endl;
	}

private:
	uint64_t m_min;
	uint64_t m_max;

	uint64_t m_acc;
	uint64_t m_num;

	std::forward_list<uint64_t> m_numbers;
};
