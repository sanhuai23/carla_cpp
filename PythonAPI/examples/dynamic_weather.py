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
        self._t += 0.008 * delta_seconds
        self._t %= 2.0 * math.pi
        self.azimuth += 0.25 * delta_seconds
        self.azimuth %= 360.0
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
        delta = (1.3 if self._increasing else -1.3) * delta_seconds
        self._t = clamp(delta + self._t, -250.0, 100.0)
        self.clouds = clamp(self._t + 40.0, 0.0, 90.0)
        self.rain = clamp(self._t, 0.0, 80.0)
        delay = -10.0 if self._increasing else 90.0
        self.puddles = clamp(self._t + delay, 0.0, 85.0)
        self.wetness = clamp(self._t * 5, 0.0, 100.0)
        self.wind = 5.0 if self.clouds <= 20 else 90 if self.clouds >= 70 else 40
        self.fog = clamp(self._t - 10, 0.0, 30.0)
        if self._t == -250.0:
            self._increasing = True
        if self._t == 100.0:
            self._increasing = False

    def __str__(self):
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
