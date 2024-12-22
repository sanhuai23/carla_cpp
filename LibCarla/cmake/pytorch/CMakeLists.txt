cmake_minimum_required(VERSION 3.5.1)# 设置CMake的最低版本要求
project(libcarla-pytorch)# 定义项目名称 

# 安装头文件  
# 使用file(GLOB)命令查找所有.h头文件，并安装到include/carla/pytorch目录下

file(GLOB libcarla_carla_pytorch_headers "${libcarla_source_path}/carla/pytorch/*.h")
install(FILES ${libcarla_carla_pytorch_headers} DESTINATION include/carla/pytorch)

# 定义libcarla_pytorch库的源文件  
# 包括.h和.cpp文件
file(GLOB libcarla_pytorch_sources
    "${libcarla_source_path}/carla/pytorch/*.h"
    "${libcarla_source_path}/carla/pytorch/*.cpp")

set(CMAKE_CUDA_COMPILER /usr/local/cuda/bin/nvcc)# 设置CUDA编译器路径
# 查找并要求Torch、TorchScatter、TorchCluster和Python3包
find_package(Torch REQUIRED)
find_package(TorchScatter REQUIRED)
find_package(TorchCluster REQUIRED)
find_package(Python3 REQUIRED)

set(PYTORCH_CPP_STD_INCLUDES "/usr/include/c++/7")# 设置PyTorch C++ API的标准库包含路径

# @todo These flags need to be compatible with setup.py compilation.
set(CMAKE_CXX_FLAGS_RELEASE "-DDEBUG -std=c++14 -O2 -fPIC -D_GLIBCXX_USE_CXX11_ABI=0 -I${PYTORCH_CPP_STD_INCLUDES}" CACHE STRING "" FORCE)
 
# ==============================================================================
# Create targets for debug and release in the same build type.
# ==============================================================================
# 根据是否定义了LIBCARLA_BUILD_RELEASE或LIBCARLA_BUILD_DEBUG来构建不同的目标
if (LIBCARLA_BUILD_RELEASE)
 # 添加静态库carla_pytorch
  add_library(carla_pytorch STATIC ${libcarla_pytorch_sources})
  # 为carla_pytorch库添加包含目录
  target_include_directories(carla_pytorch SYSTEM PRIVATE
      "${BOOST_INCLUDE_PATH}"
      "${RPCLIB_INCLUDE_PATH}")
# 添加PyTorch及其依赖库的包含目录
  # 将 ${TORCH_INCLUDE_DIRS} 所指向的目录添加到名为 carla_pytorch 的目标的包含目录中，PRIVATE 表示这是私有包含目录，SYSTEM 表示将其视为系统头文件所在目录（可能影响编译警告等处理方式）
target_include_directories(carla_pytorch PRIVATE SYSTEM "${TORCH_INCLUDE_DIRS}") 

# 将 ${TorchScatter_INCLUDE_DIR} 所指向的目录添加到 carla_pytorch 目标的包含目录中，同样是私有且视为系统头文件所在目录，用于引入 TorchScatter 相关的头文件路径
target_include_directories(carla_pytorch PRIVATE SYSTEM "${TorchScatter_INCLUDE_DIR}") 

# 将 ${TorchCluster_INCLUDE_DIR} 所指向的目录添加到 carla_pytorch 目标的包含目录中，作用是为了能正确包含 TorchCluster 相关的头文件，设置为私有且按系统头文件目录处理
target_include_directories(carla_pytorch PRIVATE SYSTEM "${TorchCluster_INCLUDE_DIR}") 

# 将 ${TorchSparse_INCLUDE_DIR} 所指向的目录添加到 carla_pytorch 目标的包含目录中，方便在编译时能找到 TorchSparse 相关的头文件，采用私有、系统头文件目录的设置方式
target_include_directories(carla_pytorch PRIVATE SYSTEM "${TorchSparse_INCLUDE_DIR}") 

# 将 ${Python3_INCLUDE_DIRS} 所指向的目录添加到 carla_pytorch 目标的包含目录中，以确保可以引入 Python3 相关的头文件，也是按私有、系统头文件目录的形式来添加
target_include_directories(carla_pytorch PRIVATE SYSTEM "${Python3_INCLUDE_DIRS}") 

# 将 ${TORCH_LIBRARIES} 所代表的库链接到 carla_pytorch 这个目标上，使得最终生成的可执行文件或库能够使用 Torch 相关的库功能
target_link_libraries(carla_pytorch "${TORCH_LIBRARIES}") # 链接PyTorch库

  install(TARGETS carla_pytorch DESTINATION lib OPTIONAL) # 安装carla_pytorch库

  set_target_properties(carla_pytorch PROPERTIES COMPILE_FLAGS "${CMAKE_CXX_FLAGS_RELEASE}")# 设置carla_pytorch的编译标志

endif()

if (LIBCARLA_BUILD_DEBUG)

  add_library(carla_pytorch_debug STATIC ${libcarla_pytorch_sources})

  target_include_directories(carla_pytorch_debug SYSTEM PRIVATE
      "${BOOST_INCLUDE_PATH}"
      "${RPCLIB_INCLUDE_PATH}")

  install(TARGETS carla_pytorch_debug DESTINATION lib OPTIONAL)

  set_target_properties(carla_pytorch_debug PROPERTIES COMPILE_FLAGS "${CMAKE_CXX_FLAGS_DEBUG}")
  target_compile_definitions(carla_pytorch_debug PUBLIC -DBOOST_ASIO_ENABLE_BUFFER_DEBUGGING)

endif()
