#pragma once
#include "DataStructs.h"

namespace MeshReconstruction
{
  struct IntersectInfo
  {
    // 0 - 255
    int signConfig;

    // 如果存在，则第i条边的顶点存储在第i个位置
    //关于边的编号和位置，请参见numberings.png
    std::array<Vec3, 12> edgeVertIndices;
  };

  class Cube
  {
    Vec3 pos[8];
    double sdf[8];

    Vec3 LerpVertex(double isoLevel, int i1, int i2) const;
    int SignConfig(double isoLevel) const;

  public:
    Cube(Rect3 const &space, Fun3s const &sdf);

    // Find the vertices where the surface intersects the cube.
    IntersectInfo Intersect(double isoLevel = 0) const;
  };

  namespace
  {
    // Cube有8个顶点。每个顶点可以有正号或负号
    // 在每种情况下，2^8=256种可能的配置映射到相交的边
    // 这12条边被编号为1,2,4,2048，并为每个配置存储为一个12位的位串
    const int signConfigToIntersectedEdges[256] = {
        0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
        0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
        0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
        0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
        0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c,
        0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
        0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac,
        0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
        0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c,
        0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
        0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc,
        0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
        0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c,
        0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
        0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc,
        0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
        0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
        0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
        0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
        0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
        0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
        0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
        0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
        0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460,
        0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
        0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0,
        0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
        0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230,
        0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
        0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190,
        0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
        0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0};

    struct Edge
    {
      int edgeFlag : 12; // flag: 1, 2, 4, ... 2048
      int vert0;         // 0-7
      int vert1;         // 0-7
    };

    const Edge edges[12] =
        {
            {1, 0, 1}, // edge 0
            {2, 1, 2}, // edge 1
            {4, 2, 3}, // ...
            {8, 3, 0},
            {16, 4, 5},
            {32, 5, 6},
            {64, 6, 7},
            {128, 7, 4},
            {256, 0, 4},
            {512, 1, 5},
            {1024, 2, 6},
            {2048, 3, 7} // edge 11
    };
  }

  Vec3 Cube::LerpVertex(double isoLevel, int i1, int i2) const
  {
    auto const Eps = 1e-5;
    auto const v1 = sdf[i1];
    auto const v2 = sdf[i2];
    auto const &p1 = pos[i1];
    auto const &p2 = pos[i2];

    if (abs(isoLevel - v1) < Eps)
      return p1;
    if (abs(isoLevel - v2) < Eps)
      return p2;
    if (abs(v1 - v2) < Eps)
      return p1;

    auto mu = (isoLevel - v1) / (v2 - v1);
    return p1 + (p2 - p1) * mu;
  }

  Cube::Cube(Rect3 const &space, Fun3s const &sdf)
  {
    auto mx = space.min.x;
    auto my = space.min.y;
    auto mz = space.min.z;

    auto sx = space.size.x;
    auto sy = space.size.y;
    auto sz = space.size.z;

    pos[0] = space.min;
    pos[1] = {mx + sx, my, mz};
    pos[2] = {mx + sx, my, mz + sz};
    pos[3] = {mx, my, mz + sz};
    pos[4] = {mx, my + sy, mz};
    pos[5] = {mx + sx, my + sy, mz};
    pos[6] = {mx + sx, my + sy, mz + sz};
    pos[7] = {mx, my + sy, mz + sz};

    for (auto i = 0; i < 8; ++i)
    {
      auto sd = sdf(pos[i]);
      if (sd == 0)
        sd += 1e-6;
      this->sdf[i] = sd;
    }
  }

  int Cube::SignConfig(double isoLevel) const
  {
    auto edgeIndex = 0;

    for (auto i = 0; i < 8; ++i)
    {
      if (sdf[i] < isoLevel)
      {
        edgeIndex |= 1 << i;
      }
    }

    return edgeIndex;
  }

  IntersectInfo Cube::Intersect(double iso) const
  {
    // idea:
    // 从立方体的8个角的符号中计算出一个符号配置(256个可能的)
    // 这个配置可以用来索引到一个表中，这个表告诉12条边中哪条是相交的
    // 找到与边相邻的顶点并插值切割顶点并将其存储在Intersectionlnfo对象中

    IntersectInfo intersect;
    intersect.signConfig = SignConfig(iso);

    // 这是一个循环结构，使用基于范围的 for 循环（C++11 及之后支持的特性），从 0 开始，每次递增 1，直到小于 12 为止，循环变量为 e。
// 这里的循环很可能是用于遍历某种与边（edges）相关的数据结构中的 12 个元素（具体要结合上下文看 edges 代表什么）。
for (auto e = 0; e < 12; ++e)
{
    // 这是一个条件判断语句，判断条件比较复杂，涉及位运算和数组访问。
    // signConfigToIntersectedEdges 应该是一个数组或者映射类型的数据结构（结合名字推测），通过 intersect.signConfig 作为索引来获取一个值，
    // 然后用这个值与 edges[e].edgeFlag 进行位与（&）运算，目的可能是检查当前的符号配置（signConfig）对应的相交边的标识（edgeFlag）是否满足某种条件，
    // 如果满足条件（即位与运算结果不为 0），则进入下面的代码块执行相应操作。
    if (signConfigToIntersectedEdges[intersect.signConfig] & edges[e].edgeFlag)
    {
        // 获取 edges[e] 这条边的起点顶点索引（vert0），这里 auto 关键字会自动根据 edges[e].vert0 的类型来推断变量 v0 的类型，
        // 这是 C++11 及之后方便的类型推导机制，方便代码书写且使代码更简洁，无需显式写出具体类型（前提是能从初始化表达式推断出唯一类型）。
        auto v0 = edges[e].vert0;
        // 同理，获取 edges[e] 这条边的终点顶点索引（vert1），并通过 auto 自动推导类型赋值给变量 v1。
        auto v1 = edges[e].vert1;

        // 调用 LerpVertex 函数，传入 iso、v0 和 v1 这三个参数，函数功能可能是根据 iso 参数以及边的两个顶点 v0 和 v1 进行线性插值计算，
        // 得到一个新的顶点（具体的插值规则和含义要根据 LerpVertex 函数的实现来确定），并将结果赋值给 vert 变量，同样使用 auto 推导类型。
        auto vert = LerpVertex(iso, v0, v1);

        // 将计算得到的新顶点索引（vert）存储到 intersect.edgeVertIndices 数组中，索引为当前遍历的边的序号 e，
        // 这样就更新了 intersect 结构体（或者类对象，同样要结合上下文确定）中与边的顶点索引相关的数据成员，方便后续使用这些计算好的数据。
        intersect.edgeVertIndices[e] = vert;
    }
}

// 函数最后返回经过上述循环处理后的 intersect 对象，这个对象可能包含了经过一系列条件判断和顶点插值计算后更新的与相交边顶点相关的数据，
// 返回值会传递回调用该函数的地方，供后续代码继续使用。
return intersect;

}
