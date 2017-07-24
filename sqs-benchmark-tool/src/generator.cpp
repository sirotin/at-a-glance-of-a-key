#include "generator.h"

#include <iostream>
#include <random>
#include <climits>
#include <algorithm>
#include <functional>

Aws::Utils::ByteBuffer generate(uint32_t sizeKB)
{
	std::cout << "Generating " << sizeKB << "KB buffer" << std::endl;

	std::independent_bits_engine<std::default_random_engine, CHAR_BIT, unsigned char> rbe;
	std::vector<unsigned char> data(sizeKB * 1024);
	std::generate(std::begin(data), std::end(data), std::ref(rbe));

	return Aws::Utils::ByteBuffer(data.data(), sizeKB * 1024);
}
