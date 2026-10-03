#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

static uint64_t factorial(unsigned n) {
  uint64_t answer = 1;
  for (unsigned i = 2; i <= n; ++i) answer *= i;
  return answer;
}

int main(int argc, char** argv) {
  try {
    if (argc != 4) throw std::runtime_error("usage: typed_kernel_histogram matrix.txt types certificate.txt");
    std::ifstream input(argv[1]);
    if (!input) throw std::runtime_error("cannot open matrix input");
    uint64_t n64 = 0, q64 = 0;
    input >> n64 >> q64;
    const unsigned long parsed_types = std::stoul(argv[2]);
    if (parsed_types == 0 || parsed_types > 16) throw std::runtime_error("invalid types");
    const uint32_t types = static_cast<uint32_t>(parsed_types);
    if (n64 == 0 || n64 > 4096 || q64 == 0 || q64 > 1000000000ULL ||
        n64 % types != 0) {
      throw std::runtime_error("invalid n/q/types");
    }
    const uint32_t n = static_cast<uint32_t>(n64);
    const uint32_t q = static_cast<uint32_t>(q64);
    const uint32_t base = n / types;
    std::vector<uint32_t> matrix(static_cast<size_t>(n) * n);
    for (size_t i = 0; i < matrix.size(); ++i) {
      uint64_t value = 0;
      if (!(input >> value) || value > q) throw std::runtime_error("invalid matrix entry");
      matrix[i] = static_cast<uint32_t>(value);
    }
    input >> std::ws;
    if (!input.eof()) throw std::runtime_error("trailing matrix input");
    for (uint32_t i = 0; i < n; ++i) {
      for (uint32_t j = 0; j < n; ++j) {
        if (matrix[static_cast<size_t>(i) * n + j] !=
            matrix[static_cast<size_t>(j) * n + i]) {
          throw std::runtime_error("asymmetric matrix");
        }
      }
    }

    std::map<std::vector<uint32_t>, uint32_t> kernel_index;
    std::vector<std::vector<uint32_t>> kernels;
    std::vector<uint32_t> blocks(static_cast<size_t>(base) * base);
    for (uint32_t a = 0; a < base; ++a) {
      for (uint32_t b = 0; b < base; ++b) {
        std::vector<uint32_t> kernel;
        kernel.reserve(static_cast<size_t>(types) * types);
        for (uint32_t s = 0; s < types; ++s) {
          for (uint32_t t = 0; t < types; ++t) {
            const uint32_t i = a * types + s;
            const uint32_t j = b * types + t;
            kernel.push_back(matrix[static_cast<size_t>(i) * n + j]);
          }
        }
        auto [it, inserted] = kernel_index.emplace(kernel, static_cast<uint32_t>(kernels.size()));
        if (inserted) kernels.push_back(kernel);
        blocks[static_cast<size_t>(a) * base + b] = it->second;
      }
    }
    const uint64_t kernel_count = kernels.size();
    if (kernel_count == 0) throw std::runtime_error("no kernels");

    auto encode = [kernel_count](const std::array<uint32_t, 6>& ids) {
      uint64_t code = 0;
      for (uint32_t id : ids) {
        if (id >= kernel_count ||
            code > (std::numeric_limits<uint64_t>::max() - id) / kernel_count) {
          throw std::runtime_error("kernel signature does not fit UInt64");
        }
        code = code * kernel_count + id;
      }
      return code;
    };
    auto decode = [kernel_count](uint64_t code) {
      std::array<uint32_t, 6> ids{};
      for (int i = 5; i >= 0; --i) {
        ids[static_cast<size_t>(i)] = static_cast<uint32_t>(code % kernel_count);
        code /= kernel_count;
      }
      return ids;
    };

    std::unordered_map<uint64_t, uint64_t> histogram;
    histogram.reserve(8192);
    uint64_t mass = 0;
    for (uint32_t a = 0; a < base; ++a) {
      for (uint32_t b = a; b < base; ++b) {
        for (uint32_t c = b; c < base; ++c) {
          for (uint32_t d = c; d < base; ++d) {
            const std::array<uint32_t, 4> vertices{a, b, c, d};
            uint64_t weight = 24;
            unsigned run = 1;
            for (unsigned i = 1; i <= 4; ++i) {
              if (i < 4 && vertices[i] == vertices[i - 1]) {
                ++run;
              } else {
                weight /= factorial(run);
                run = 1;
              }
            }
            const std::array<uint32_t, 6> ids{
                blocks[static_cast<size_t>(a) * base + b],
                blocks[static_cast<size_t>(a) * base + c],
                blocks[static_cast<size_t>(a) * base + d],
                blocks[static_cast<size_t>(b) * base + c],
                blocks[static_cast<size_t>(b) * base + d],
                blocks[static_cast<size_t>(c) * base + d]};
            histogram[encode(ids)] += weight;
            mass += weight;
          }
        }
      }
    }
    uint64_t expected_mass = 1;
    for (unsigned i = 0; i < 4; ++i) expected_mass *= base;
    if (mass != expected_mass) throw std::runtime_error("coarse histogram mass mismatch");

    std::vector<std::pair<uint64_t, uint64_t>> rows(histogram.begin(), histogram.end());
    std::sort(rows.begin(), rows.end());
    std::ofstream output(argv[3], std::ios::out | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create certificate");
    output << n << ' ' << q << ' ' << base << ' ' << types << ' '
           << kernels.size() << ' ' << rows.size() << '\n';
    for (const auto& kernel : kernels) {
      for (size_t i = 0; i < kernel.size(); ++i) {
        if (i) output << ' ';
        output << kernel[i];
      }
      output << '\n';
    }
    for (const auto& [code, count] : rows) {
      const auto ids = decode(code);
      for (uint32_t id : ids) output << id << ' ';
      output << count << '\n';
    }
    output.close();
    if (!output) throw std::runtime_error("certificate write failed");
    std::cout << n << ' ' << q << ' ' << base << ' ' << types << ' '
              << kernels.size() << ' ' << rows.size() << ' ' << mass << '\n';
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
  return 0;
}
