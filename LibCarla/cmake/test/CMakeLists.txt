# LibCarla的单元测试
cmake_minimum_required(VERSION 3.5.1)
project(libcarla-unit-tests)

# 进行客户端的测试
if (CMAKE_BUILD_TYPE STREQUAL "Client")
  set(carla_config client)
# 进行服务端的测试
elseif (CMAKE_BUILD_TYPE STREQUAL "Server")
  set(carla_config server)
endif ()
# 是否构建责任敏感安全库
if (BUILD_RSS_VARIANT)
  set(carla_target_postfix "_rss")
else()
  set(carla_target_postfix "")
endif()

# 需要添加到链接库搜索路径的目录：
# 远程过程调用(Remote Procedure Call, RPC)、Google Test 库
link_directories(
    ${RPCLIB_LIB_PATH}
    ${GTEST_LIB_PATH})

# GLOB 会产生一个由所有匹配表达式的文件组成的列表，并将其保存到libcarla_test_sources变量中
# 包括 性能剖析器 和 测试模块（客户端/服务端）中的所有C++代码
# 使用 file(GLOB) 命令来收集一系列文件路径，将匹配的文件路径列表存储在变量 libcarla_test_sources 中。
# 这里收集的是 ${libcarla_source_path}/carla/profiler/ 目录下所有的.cpp 和.h 文件，也就是收集与性能分析器（profiler）相关的代码文件和头文件。
file(GLOB libcarla_test_sources
    "${libcarla_source_path}/carla/profiler/*.cpp"
    "${libcarla_source_path}/carla/profiler/*.h"
)

# 继续向 libcarla_test_sources 变量中添加文件路径，这次收集的是 ${libcarla_source_path}/test/ 目录下所有的.cpp 和.h 文件，
# 通常这里面会包含各种通用的测试相关的代码文件和头文件。
file(GLOB libcarla_test_sources
    # 上一轮收集的文件路径已经在变量中，这里继续追加新的匹配路径
    APPEND
    "${libcarla_source_path}/test/*.cpp"
    "${libcarla_source_path}/test/*.h"
)

# 再向 libcarla_test_sources 变量中添加文件路径，这次收集的是 ${libcarla_source_path}/test/${carla_config}/ 目录下的所有.cpp 和.h 文件，
# 其中 ${carla_config} 应该是一个自定义的配置相关变量，意味着会根据不同的配置收集对应测试目录下的代码文件和头文件。
file(GLOB libcarla_test_sources
    # 同样是追加新的匹配路径到变量中
    APPEND
    "${libcarla_source_path}/test/${carla_config}/*.cpp"
    "${libcarla_source_path}/test/${carla_config}/*.h"
)

# 最后向 libcarla_test_sources 变量中添加文件路径，收集的是 ${libcarla_source_path}/test/common/ 目录下所有的.cpp 和.h 文件，
# 这里的 common 目录通常存放一些多个测试都可能会用到的通用代码文件和头文件。
file(GLOB libcarla_test_sources
    # 继续追加路径到变量中
    APPEND
    "${libcarla_source_path}/test/common/*.cpp"
    "${libcarla_source_path}/test/common/*.h"
)

# 同样使用 file(GLOB) 命令，不过这里是初始化一个空的文件路径列表存储在变量 libcarla_test_client_sources 中，
# 可能后续会根据实际情况往这个变量里添加具体与测试客户端相关的文件路径，目前是空的状态。
file(GLOB libcarla_test_client_sources "")

# 如果LibCarla使用调试版本，则libcarla_test也是用调试版本
if (LIBCARLA_BUILD_DEBUG)
  list(APPEND build_targets libcarla_test_${carla_config}_debug)
endif()

# 如果LibCarla使用发布版本，则libcarla_test也是用发布版本
if (LIBCARLA_BUILD_RELEASE)
  list(APPEND build_targets libcarla_test_${carla_config}_release)
endif()

# 以相同的构建类型创建调试和发布的对象
foreach(target ${build_targets})

  add_executable(${target} ${libcarla_test_sources})

  target_compile_definitions(${target} PUBLIC
      -DLIBCARLA_ENABLE_PROFILER
      -DLIBCARLA_WITH_GTEST)

  target_include_directories(${target} SYSTEM PRIVATE
      "${BOOST_INCLUDE_PATH}"
      "${RPCLIB_INCLUDE_PATH}"
      "${GTEST_INCLUDE_PATH}"
      "${LIBPNG_INCLUDE_PATH}")

  target_include_directories(${target} PRIVATE
      "${libcarla_source_path}/test")

  if (WIN32)
      target_link_libraries(${target} "gtest_main.lib")
      target_link_libraries(${target} "gtest.lib")
      target_link_libraries(${target} "rpc.lib")
  else()
      target_link_libraries(${target} "-lrpc")
      target_link_libraries(${target} "-lgtest_main")
      target_link_libraries(${target} "-lgtest")
  endif()

  install(TARGETS ${target} DESTINATION test OPTIONAL)
endforeach(target)

# 构建调试版本
# 判断是否定义了 LIBCARLA_BUILD_DEBUG 变量，若该变量为真（通常用于标识构建调试版本），则执行下面花括号内的代码块。
# 这意味着下面的设置都是针对调试版本构建时的特定配置。
if (LIBCARLA_BUILD_DEBUG)
    # 以下是针对调试版本的特定选项设置部分的注释说明

    # 设置名为 libcarla_test_${carla_config}_debug 的目标（可能是可执行文件或者库等）的编译属性，
    # 将编译标志（COMPILE_FLAGS）设置为 ${CMAKE_CXX_FLAGS_DEBUG}，也就是使用 CMake 中预定义的 C++ 调试编译标志，
    # 例如可能包含了开启调试信息生成、关闭优化等适合调试场景的编译选项。
    set_target_properties(libcarla_test_${carla_config}_debug PROPERTIES COMPILE_FLAGS "${CMAKE_CXX_FLAGS_DEBUG}")

    # 将名为 "carla_${carla_config}${carla_target_postfix}_debug" 的库链接到 libcarla_test_${carla_config}_debug 目标上，
    # 这使得在构建 libcarla_test_${carla_config}_debug 时可以使用 "carla_${carla_config}${carla_target_postfix}_debug" 库中提供的功能，
    # 其中 ${carla_config} 和 ${carla_target_postfix} 应该是项目中自定义的配置相关和目标后缀相关的变量。
    target_link_libraries(libcarla_test_${carla_config}_debug "carla_${carla_config}${carla_target_postfix}_debug")

    # 为 libcarla_test_${carla_config}_debug 目标添加编译定义（COMPILE_DEFINITIONS），这里定义了 BOOST_ASIO_ENABLE_BUFFER_DEBUGGING，
    # 表示在编译时开启 Boost.Asio 库中缓冲区相关的调试功能（如果使用了 Boost.Asio 库的话），这样有助于排查相关的问题。
    target_compile_definitions(libcarla_test_${carla_config}_debug PUBLIC -DBOOST_ASIO_ENABLE_BUFFER_DEBUGGING)

    # 再进行一个条件判断，判断当前的 CMake 构建类型（CMAKE_BUILD_TYPE）是否等于 "Client"，如果是客户端构建类型，则执行下面花括号内的代码。
    if (CMAKE_BUILD_TYPE STREQUAL "Client")
        # 将位于 ${BOOST_LIB_PATH} 目录下的 libboost_filesystem.a 库链接到 libcarla_test_${carla_config}_debug 目标上，
        # 这使得在客户端构建的调试版本中可以使用 Boost 文件系统库（libboost_filesystem.a）的功能，
        # 例如进行文件操作相关的处理等，前提是项目中依赖了该库。
        target_link_libraries(libcarla_test_${carla_config}_debug "${BOOST_LIB_PATH}/libboost_filesystem.a")
    endif()
endif()

# 构建发布版本
if (LIBCARLA_BUILD_RELEASE)
  # Specific options for release.
  set_target_properties(libcarla_test_${carla_config}_release PROPERTIES COMPILE_FLAGS "${CMAKE_CXX_FLAGS_RELEASE}")
  target_link_libraries(libcarla_test_${carla_config}_release "carla_${carla_config}${carla_target_postfix}")
  if (CMAKE_BUILD_TYPE STREQUAL "Client")
      target_link_libraries(libcarla_test_${carla_config}_release "${BOOST_LIB_PATH}/libboost_filesystem.a")
  endif()
endif()
