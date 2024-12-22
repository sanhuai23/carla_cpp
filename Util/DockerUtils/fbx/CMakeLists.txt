# use: ./build/cmake .. -A x64
# Download from: https://www.autodesk.com/content/dam/autodesk/www/adn/fbx/2020-0-1/fbx202001_fbxsdk_linux.tar.gz
# Dependencies:
#	sudo apt-get install libxml2-dev

# 指定 CMake 构建所需的最低版本要求为 2.8.9，意味着使用的 CMake 版本必须大于等于这个版本，
# 这样才能保证后续使用的 CMake 相关功能可以正常工作，低于此版本可能会出现不兼容或功能缺失的情况。
cmake_minimum_required(VERSION 2.8.9)

# 创建一个名为 FBX2OBJ 的 CMake 项目，后续的所有配置（如添加源文件、链接库等操作）都将围绕这个项目展开。
project(FBX2OBJ)

# 设置 CMake 生成器平台为 x64，这通常用于指定生成的目标文件（例如可执行文件或者库）所针对的目标平台架构，
# 确保构建出来的内容是适用于 64 位操作系统环境的，不同的生成器（如 Makefile、Visual Studio 等）会根据此设置来生成相应的平台相关的构建文件。
set(CMAKE_GENERATOR_PLATFORM x64)

# 尝试查找名为 LibXml2 的库，如果找不到该库，会导致 CMake 配置阶段报错，因为使用了 REQUIRED 关键字，
# 若找到该库，CMake 会自动设置好相应的包含目录、库文件路径等相关变量，方便后续链接等操作使用，不过此处代码被注释掉了，暂未生效。
# find_package(LibXml2 REQUIRED)

# 将 "src" 目录添加到项目的包含目录列表中，这样在编译项目的源文件时，编译器就能正确找到位于 "src" 目录下的头文件，
# 例如源文件中使用 #include 指令包含该目录下的头文件时，编译器可以顺利解析。
include_directories(src)

# 将 "dependencies/include" 目录添加到项目的包含目录列表中，一般来说这个目录存放着项目所依赖的第三方库或者其他模块的头文件，
# 把它添加进来能保证编译过程中可以顺利找到这些外部依赖的头文件内容，确保编译顺利进行。
include_directories(dependencies/include)

# 将 "dependencies/lib/gcc/x64/release" 目录添加到项目的链接目录列表中，意味着当链接目标文件（如生成可执行文件时链接各种库）时，
# CMake 会在这个目录下去查找所需的库文件，方便找到项目依赖的外部库来进行链接操作。
link_directories(dependencies/lib/gcc/x64/release)

# 使用 file(GLOB) 命令来收集所有位于 "src" 目录下以 ".cpp" 为后缀的文件路径，并将这些文件路径存储在变量 SOURCES 中，
# 这样后续就可以方便地使用这个变量来指定项目的源文件列表，例如用于创建可执行文件或者库等操作。
file(GLOB SOURCES "src/*.cpp")

# 创建一个名为 FBX2OBJ 的可执行文件目标，使用之前收集到的源文件列表（变量 SOURCES 中的文件）进行编译构建，
# 也就是将这些源文件编译链接在一起生成最终的可执行文件，其名称与项目名相同，为 FBX2OBJ。
add_executable(FBX2OBJ ${SOURCES})

# 指定安装目标，即当执行 CMake 安装命令（例如 "make install" 等，具体取决于生成器和构建系统）时，
# 会把名为 FBX2OBJ 的目标（这里是可执行文件）安装到 "${CMAKE_CURRENT_SOURCE_DIR}/../dist" 目录下，
# 这个目录可以根据实际需求进行调整，用于部署生成的可执行文件到指定位置。
install(TARGETS FBX2OBJ DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/../dist")

# 将名为 fbxsdk 的库链接到 FBX2OBJ 这个可执行文件目标上，使得最终生成的可执行文件在运行时能够使用 fbxsdk 库所提供的功能，
# 例如调用库中的函数、使用库中定义的数据结构等，这是构建可执行文件时整合外部库依赖的关键步骤。
target_link_libraries(FBX2OBJ fbxsdk)

# 将名为 dl 的库链接到 FBX2OBJ 可执行文件目标上，具体功能取决于 dl 库本身，一般来说可能与动态链接相关的操作有关，
# 例如在运行时加载动态库等功能，不同操作系统下 dl 库的作用可能略有差异，但都是为了让项目能正常使用相关的系统级功能。
target_link_libraries(FBX2OBJ dl)

# 将名为 z 的库链接到 FBX2OBJ 可执行文件目标上，z 库通常用于处理压缩相关的功能（比如常见的 zlib 库），
# 如果项目中有涉及到数据压缩、解压缩等操作且依赖该库，通过这一步链接就能确保相应功能可以正常使用。
target_link_libraries(FBX2OBJ z)

# 将名为 xml2 的库链接到 FBX2OBJ 可执行文件目标上，这个库应该是用于处理 XML 相关操作的（可能是 LibXml2 库对应的实际链接名称），
# 使得项目在运行时能够进行 XML 文件的解析、生成等操作，前提是项目中有这方面的需求且相关代码调用了该库的功能。
target_link_libraries(FBX2OBJ xml2)
