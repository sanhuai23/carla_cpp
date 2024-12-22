#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
CARLA Dynamic Weather:

Connect to a CARLA Simulator instance and control the weather. Change Sun
position smoothly with time and generate storms occasionally.
"""

import glob
import os
import sys

try:
    # 尝试执行以下操作块，目的是将特定的路径添加到Python的模块搜索路径 `sys.path` 中，使得Python解释器能够在该路径下查找并导入相应的模块。

    # 使用 `glob.glob` 函数来查找符合特定模式的文件路径。
    # 这里构建的文件路径模式字符串为 `../carla/dist/carla-*%d.%d-%s.egg`，其中 `%d.%d-%s` 是格式化字符串占位符，会被替换为具体的值来匹配实际的文件路径。
    # `sys.version_info.major` 用于获取当前Python版本的主版本号（例如Python 3.8中的3），`sys.version_info.minor` 则获取Python版本的次版本号（例如Python 3.8中的8）。
    # 通过 `'win-amd64' if os.name == 'nt' else 'linux-x86_64'` 这样的条件表达式来根据操作系统类型进行适配，若操作系统是Windows（`os.name == 'nt'`），则 `%s` 会被替换为 `win-amd64`，否则（即操作系统为类Unix系统，如Linux）替换为 `linux-x86_64`。
    # 最终，`glob.glob` 函数会在 `../carla/dist/` 目录下查找类似 `carla-<版本号>-<操作系统架构>.egg` 这种格式的文件路径，并返回一个包含所有匹配结果的列表（这个列表可能为空，也可能包含一个或多个元素）。
    paths = glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))
    # 从 `glob.glob` 函数返回的路径列表中取出第一个元素（索引为0的元素），并将其添加到 `sys.path` 中。
    # 这里假设 `glob.glob` 返回的列表至少有一个元素，如果列表为空，那么下面这行代码尝试访问 `paths[0]` 时就会抛出 `IndexError` 异常。
    sys.path.append(paths[0])
except IndexError:
    # 如果在上述 `try` 块的代码执行过程中抛出了 `IndexError` 异常（也就是 `glob.glob` 没有找到匹配的文件路径，返回的列表为空，导致访问 `paths[0]` 出错），
    # 那么就会进入这个 `except` 块进行异常处理。在这里使用 `pass` 语句，表示不进行任何具体的操作，直接跳过异常处理，程序会继续往下执行，只是不会成功添加路径到 `sys.path` 而已。
    pass

import carla

import argparse
import math


def clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(value, maximum))


# 定义一个名为 `Sun` 的类，它继承自Python内置的 `object` 基类。这个类可能用于模拟太阳相关的属性和行为（例如在图形渲染、模拟现实场景等场景中使用）。
class Sun(object):
    # 定义类的构造函数（初始化方法），在创建 `Sun` 类的实例时会被调用，用于初始化对象的属性。
    # 构造函数接收两个参数：`azimuth` 和 `altitude`，这两个参数通常用于表示太阳在天空中的方位角和高度角信息（方位角可以理解为太阳相对于某个参考方向的水平角度，高度角表示太阳相对于地平线的垂直角度，常用于天文学、地理信息系统、图形学等领域来定位太阳位置）。
    def __init__(self, azimuth, altitude):
        # 将传入构造函数的 `azimuth` 参数值赋给对象的 `azimuth` 属性，通过这种方式，实例对象可以保存并访问太阳的方位角信息。
        self.azimuth = azimuth
        # 同样地，把传入的 `altitude` 参数值赋给对象的 `altitude` 属性，以便后续能获取太阳的高度角信息。
        self.altitude = altitude
        # 定义一个名为 `_t` 的私有属性（按照Python的命名约定，以下划线开头的属性通常被视为私有属性，虽然Python并没有真正的强制私有机制，但这是一种约定俗成的表示方式），并初始化为 `0.0`。
        # 这个属性的具体用途可能因具体应用场景而异，也许用于记录时间相关的信息（比如模拟太阳随着时间变化的情况时，可能表示时间戳或者时间进度等），但从当前代码看它初始被设置为 `0.0`。
        self._t = 0.0

    def tick(self, delta_seconds):
    # `tick` 函数可能用于模拟太阳相关属性随时间的更新操作，它接收一个参数 `delta_seconds`，这个参数通常表示时间间隔（单位可能是秒），用于体现从上一次更新到当前这次更新所经过的时间。

    # 根据传入的时间间隔 `delta_seconds` 来更新私有属性 `_t` 的值。
    # 这里将 `_t` 的值增加 `0.008 * delta_seconds`，从这个计算可以推测 `_t` 可能与某种时间相关的变化率或者角度变化有关（乘以一个较小的系数 `0.008` 可能是基于特定的模拟规则或物理模型来调整变化的幅度），每次调用 `tick` 函数时，`_t` 都会基于时间间隔进行相应的累加变化。
    self._t += 0.008 * delta_seconds
    # 对更新后的 `_t` 值进行取模运算，使其值始终保持在 `0` 到 `2.0 * math.pi`（即 `0` 到一个完整的圆周对应的弧度值，大约是 `6.28`）范围内。
    # 这样的操作常用于循环变化的属性模拟中，比如角度属性在一圈一圈循环变化时，通过取模可以保证其值不会无限制增大，而是在一个周期内循环，符合周期性变化的逻辑（例如模拟太阳在天空中角度周期性变化的情况）。
    self._t %= 2.0 * math.pi
    # 根据时间间隔 `delta_seconds` 来更新太阳的方位角 `azimuth` 属性。
    # 这里将 `azimuth` 的值增加 `0.25 * delta_seconds`，意味着方位角会随着时间以一定的速率进行变化（速率为每秒钟增加 `0.25` 度，这里可以推测方位角的单位是度，具体单位需结合整体应用场景确定），同样体现了方位角随时间动态变化的模拟逻辑。
    self.azimuth += 0.25 * delta_seconds
    # 对更新后的方位角 `azimuth` 值进行取模运算，使其始终保持在 `0` 到 `360.0` 度的范围内，这符合方位角在现实中一圈为 `360` 度的周期性特征，保证方位角的值不会超出合理的范围，模拟出方位角循环变化的效果（例如太阳在天空中绕一圈后又回到起始方位的情况）。
    self.azimuth %= 360.0
    # 根据更新后的 `_t` 值来计算并更新太阳的高度角 `altitude` 属性。
    # 使用了正弦函数 `math.sin(self._t)` 来计算高度角，乘以 `70` 并减去 `20`，从这个计算式可以看出，高度角的变化与 `_t` 的正弦值相关，并且通过系数 `70` 和 `-20` 进行了特定的缩放和偏移调整，以此来模拟太阳高度角随着某种内部计时（通过 `_t` 体现）的周期性变化情况，使得高度角在 `[-20, 50]` 这个大致范围内变化（因为正弦函数的值域是 `[-1, 1]`），符合太阳在天空中高度角的周期性起伏变化规律（例如从日出时较低慢慢升高到中午达到较高值，再慢慢降低的过程模拟）。
    self.altitude = (70 * math.sin(self._t)) - 20

    def __str__(self):
        return 'Sun(alt: %.2f, azm: %.2f)' % (self.altitude, self.azimuth)


class Storm(object):
    def __init__(self, precipitation):
        self._t = precipitation if precipitation > 0.0 else -50.0
        self._increasing = True
        self.clouds = 0.0
        self.rain = 0.0
        self.wetness = 0.0
        self.puddles = 0.0
        self.wind = 0.0
        self.fog = 0.0

    def tick(self, delta_seconds):
    # `tick` 函数可能用于模拟天气或环境相关属性随时间变化的更新操作，它接收一个参数 `delta_seconds`，这个参数通常表示时间间隔（单位可能是秒），用于体现从上一次更新到当前这次更新所经过的时间。

    # 根据当前对象的 `_increasing` 属性来确定一个变化量 `delta` 的值。
    # 如果 `_increasing` 为 `True`，则 `delta` 的值为 `1.3 * delta_seconds`，表示相关属性要正向增加；如果 `_increasing` 为 `False`，则 `delta` 的值为 `-1.3 * delta_seconds`，意味着相关属性要反向减少。这里的 `1.3` 是设定的一个变化速率系数，用于控制属性随时间变化的快慢程度。
    delta = (1.3 if self._increasing else -1.3) * delta_seconds

    # 使用 `clamp` 函数（假设 `clamp` 函数是一个用于限制值在特定区间内的自定义函数或外部引入函数）对 `delta + self._t` 的结果进行限制，使其值始终保持在 `-250.0` 到 `100.0` 这个区间内。
    # 这意味着 `self._t` 在更新时，会基于前面计算的 `delta` 进行变化，但不会超出这个规定的范围，保证了 `self._t` 这个属性值的有效性和合理性，可能 `self._t` 是一个综合影响多种天气或环境属性的基础变量。
    self._t = clamp(delta + self._t, -250.0, 100.0)

    # 根据更新后的 `self._t` 值来计算并更新 `self.clouds` 属性的值，同样使用 `clamp` 函数将计算结果限制在 `0.0` 到 `90.0` 的区间内。
    # 从计算式 `self._t + 40.0` 可以推测，`self.clouds` 的值与 `self._t` 有一定关联，并且加上 `40.0` 以及进行区间限制后，能使其符合该属性表示云量（或与云相关的某种量化指标）在合理范围内变化的要求，例如 `0` 可能表示无云，`90` 表示多云等情况（具体含义需结合整体应用场景确定）。
    self.clouds = clamp(self._t + 40.0, 0.0, 90.0)

    # 按照更新后的 `self._t` 值来更新 `self.rain` 属性的值，使用 `clamp` 函数把值限定在 `0.0` 到 `80.0` 的区间内。
    # 说明 `self.rain` 属性（可能表示降雨量或降雨概率等与雨相关的量化指标）与 `self._t` 直接相关，通过这样的限制确保其值在符合实际意义的范围内变化，比如 `0` 表示无雨，`80` 表示较大降雨情况等（具体含义取决于应用场景）。
    self.rain = clamp(self._t, 0.0, 80.0)

    # 根据当前对象的 `_increasing` 属性来确定 `delay` 的值。
    # 如果 `_increasing` 为 `False`，则 `delay` 的值为 `-10.0`；如果 `_increasing` 为 `True`，则 `delay` 的值为 `90.0`。这个 `delay` 值后续会用于计算 `self.puddles` 属性，可能用于体现不同变化趋势下对积水情况的不同影响因素（具体作用需结合完整逻辑分析）。
    delay = -10.0 if self._increasing else 90.0

    # 使用更新后的 `self._t` 和前面确定的 `delay` 值来计算并更新 `self.puddles` 属性的值，通过 `clamp` 函数将其限制在 `0.0` 到 `85.0` 的区间内。
    # 由此推测 `self.puddles` 属性（可能表示地面的积水情况或积水相关的量化指标）与 `self._t` 和 `delay` 有关，并且限制在合理区间内，使得积水情况能符合实际场景中的合理变化范围，比如 `0` 表示无积水，`85` 表示较多积水等情况（具体含义结合整体应用来看）。
    self.puddles = clamp(self._t + delay, 0.0, 85.0)

    # 根据更新后的 `self._t` 值来计算并更新 `self.wetness` 属性的值，将 `self._t` 乘以 `5` 后再通过 `clamp` 函数限制在 `0.0` 到 `100.0` 的区间内。
    # 可以推断 `self.wetness` 属性（可能表示环境的潮湿程度或物体表面的湿润程度等相关量化指标）与 `self._t` 有倍数关系，并且通过区间限制保证其在合理的百分比范围（`0%` - `100%`）内变化，符合表示湿度情况的实际意义。
    self.wetness = clamp(self._t * 5, 0.0, 100.0)

    # 根据 `self.clouds` 属性的值来确定 `self.wind` 属性的值。
    # 如果 `self.clouds` 的值小于等于 `20`，则 `self.wind` 的值设定为 `5.0`；如果 `self.clouds` 的值大于等于 `70`，则 `self.wind` 的值设定为 `90`；否则（即 `20 < self.clouds < 70`），`self.wind` 的值设定为 `40`。这表明 `self.wind`（可能表示风速或风力相关的量化指标）与云量情况存在关联，按照不同的云量区间设定不同的风速值，模拟出天气因素之间相互影响的效果（具体数值对应的实际风速情况需结合应用场景确定）。
    self.wind = 5.0 if self.clouds <= 20 else 90 if self.clouds >= 70 else 40

    # 根据更新后的 `self._t` 值来计算并更新 `self.fog` 属性的值，通过 `clamp` 函数将 `self._t - 10` 的结果限制在 `0.0` 到 `30.0` 的区间内。
    # 说明 `self.fog` 属性（可能表示雾的浓度或能见度相关的量化指标）与 `self._t` 相关，并且经过这样的计算和区间限制，使其符合雾在实际场景中合理的变化范围，例如 `0` 表示无雾，`30` 表示浓雾等情况（具体含义结合整体应用判断）。
    self.fog = clamp(self._t - 10, 0.0, 30.0)

    # 判断 `self._t` 的值是否等于 `-250.0`，如果是，则将 `_increasing` 属性设置为 `True`。
    # 这可能意味着当 `self._t` 达到下限值时，相关属性要开始正向增加，改变整体的变化趋势，用于控制天气或环境属性循环变化的逻辑（例如模拟从恶劣天气逐渐变好的转折点）。
    if self._t == -250.0:
        self._increasing = True

    # 判断 `self._t` 的值是否等于 `100.0`，如果是，则将 `_increasing` 属性设置为 `False`。
    # 与上面的逻辑相对应，当 `self._t` 达到上限值时，相关属性要开始反向减少，实现天气或环境属性在规定范围内来回变化的模拟效果（例如模拟从较好天气逐渐变差的转折点）。
    if self._t == 100.0:
        self._increasing = False

    def __str__(self):
    # `__str__` 是Python中的一个特殊方法（也叫魔术方法），当使用 `print()` 函数打印对象或者将对象转换为字符串（例如使用 `str()` 函数）时，这个方法会被自动调用。
    # 它的主要作用是定义对象的字符串表示形式，方便开发者直观地查看对象的相关属性信息，以一种友好的、易于阅读的方式呈现对象的关键内容。

    # 通过字符串格式化的方式构建并返回一个字符串，这个字符串描述了与当前对象相关的部分天气属性信息，格式为 'Storm(clouds=%d%%, rain=%d%%, wind=%d%%)'。
    # 其中 `%d` 是格式化占位符，表示要替换为整数类型的数据，`%%` 用于在字符串中输出一个 `%` 符号（因为 `%` 在格式化字符串中有特殊含义，所以要输出它自身需要使用 `%%` 转义）。
    # 这里分别将对象的 `self.clouds`、`self.rain` 和 `self.wind` 属性的值按照顺序替换到对应的占位符位置，从而生成一个形如 'Storm(clouds=30%, rain=20%, wind=50%)' 的字符串（这里的 `30`、`20`、`50` 只是示例数值，实际由对应属性的真实值决定）。
    # 最终返回的这个字符串就是该对象在被转换为字符串或者打印时呈现给用户的内容，用于展示当前对象所代表的天气状况中云量、降雨量和风速这几个关键属性的百分比情况。
    return 'Storm(clouds=%d%%, rain=%d%%, wind=%d%%)' % (self.clouds, self.rain, self.wind)


class Weather(object):
    def __init__(self, weather):
        self.weather = weather
        self._sun = Sun(weather.sun_azimuth_angle, weather.sun_altitude_angle)
        self._storm = Storm(weather.precipitation)

    def tick(self, delta_seconds):
        self._sun.tick(delta_seconds)
        self._storm.tick(delta_seconds)
        self.weather.cloudiness = self._storm.clouds
        self.weather.precipitation = self._storm.rain
        self.weather.precipitation_deposits = self._storm.puddles
        self.weather.wind_intensity = self._storm.wind
        self.weather.fog_density = self._storm.fog
        self.weather.wetness = self._storm.wetness
        self.weather.sun_azimuth_angle = self._sun.azimuth
        self.weather.sun_altitude_angle = self._sun.altitude

    def __str__(self):
        return '%s %s' % (self._sun, self._storm)


def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-s', '--speed',
        metavar='FACTOR',
        default=1.0,
        type=float,
        help='rate at which the weather changes (default: 1.0)')
    args = argparser.parse_args()

    speed_factor = args.speed
    update_freq = 0.1 / speed_factor

    client = carla.Client(args.host, args.port)
    client.set_timeout(2.0)
    world = client.get_world()

    weather = Weather(world.get_weather())

    elapsed_time = 0.0

    while True:
        timestamp = world.wait_for_tick(seconds=30.0).timestamp
        elapsed_time += timestamp.delta_seconds
        if elapsed_time > update_freq:
            weather.tick(speed_factor * elapsed_time)
            world.set_weather(weather.weather)
            sys.stdout.write('\r' + str(weather) + 12 * ' ')
            sys.stdout.flush()
            elapsed_time = 0.0


if __name__ == '__main__':

    main()
