import glob
import os
import sys

try:
    # 尝试执行以下代码块内容，目的是查找符合特定格式的文件路径，并将其添加到Python的模块搜索路径 `sys.path` 中，使得Python能够正确导入对应的模块（这里大概率是与 `carla` 相关的模块）。

    # 使用 `glob.glob` 函数来查找满足特定模式的文件路径。
    # 此处构建的文件路径模式字符串是 `../carla/dist/carla-*%d.%d-%s.egg`，其中 `%d.%d-%s` 属于格式化字符串占位符，会依据后面给定的具体值来替换，从而生成实际要查找的文件路径模式。
    # `sys.version_info.major` 用于获取当前Python版本的主版本号（例如在Python 3.9中，主版本号就是 `3`），`sys.version_info.minor` 则用来获取Python版本的次版本号（例如Python 3.9中，次版本号就是 `9`）。
    # 通过 `'win-amd64' if os.name == 'nt' else 'linux-x86_64'` 这个条件表达式，依据操作系统的类型来确定最后一部分的替换内容：
    # 如果当前操作系统是Windows（在Python中，通过 `os.name == 'nt'` 来判断是否为Windows系统），那么 `%s` 就会被替换成 `win-amd64`；若操作系统不是Windows（即类Unix系统，比如Linux，此时 `os.name` 的值不为 `nt`），`%s` 则会被替换为 `linux-x86_64`。
    # 最终，`glob.glob` 函数会在 `../carla/dist/` 目录下，查找类似 `carla-<Python版本号>-<操作系统架构>.egg` 这种格式的文件路径，并返回一个包含所有匹配结果的列表（这个列表有可能是空的，也可能包含一个或多个元素）。
    paths = glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))
    # 从 `glob.glob` 函数返回的路径列表里取出第一个元素（也就是索引为 `0` 的元素），然后将其添加到 `sys.path` 中。
    # 这里默认 `glob.glob` 返回的列表至少要有一个元素，如果该列表为空，那么执行 `paths[0]` 这一步时就会抛出 `IndexError` 异常，因为无法获取一个不存在的索引位置上的元素。
    sys.path.append(paths[0])
except IndexError:
    # 如果在上述 `try` 块中的代码执行时抛出了 `IndexError` 异常（也就是 `glob.glob` 没有找到匹配的文件路径，返回的列表为空，导致访问 `paths[0]` 出现错误），
    # 那么程序就会进入到这个 `except` 块中进行异常处理。在这里使用了 `pass` 语句，意味着不会执行任何实质性的操作，只是简单地跳过这个异常处理过程，让程序继续往下执行，不过这样就没办法成功地把相应路径添加到 `sys.path` 里面了。
    # 这种处理方式相对比较简单，在实际应用场景中，可能需要根据具体情况考虑是否要给出更合适的提示信息，比如提示用户找不到对应的 `carla` 模块文件，或者采取其他更完善的错误处理策略，以更好地应对这种找不到文件路径的情况。
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

client = carla.Client('localhost', 2000)
world = client.get_world()

location = carla.Location(200.0, 200.0, 200.0)
rotation = carla.Rotation(0.0, 0.0, 0.0)
transform = carla.Transform(location, rotation)

bp_library = world.get_blueprint_library()
bp_audi = bp_library.find('vehicle.audi.tt')
audi = world.spawn_actor(bp_audi, transform)

component_transform = audi.get_component_world_transform('front-blinker-r-1')
print(component_transform)

