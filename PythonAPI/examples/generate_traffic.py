#!/usr/bin/env python

# Copyright (c) 2021 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example script to generate traffic in the simulation"""

import glob
import os
import sys
import time

try:
    # 尝试执行以下代码块。这段代码的主要目的是将特定路径添加到Python的模块搜索路径 `sys.path` 中，使得Python解释器能够找到并导入对应的模块，这里的模块大概率与 `carla` 相关。

    # 使用 `glob.glob` 函数来查找符合特定模式的文件路径。
    # 构建的文件路径模式字符串为 `../carla/dist/carla-*%d.%d-%s.egg`，其中 `%d.%d-%s` 是格式化字符串占位符，会被替换为具体的值。
    # `sys.version_info.major` 用于获取当前Python版本的主版本号（例如Python 3.8 中，主版本号就是3），`sys.version_info.minor` 获取Python版本的次版本号（例如Python 3.8 中，次版本号就是8）。
    # 通过 `'win-amd64' if os.name == 'nt' else 'linux-x86_64'` 这样的条件表达式，根据操作系统类型进行适配：
    # 如果操作系统是Windows（在Python中，`os.name == 'nt'` 表示Windows系统），那么 `%s` 会被替换为 `win-amd64`；如果是其他操作系统（通常是类Unix系统，如Linux，此时 `os.name` 的值不是 `nt`），`%s` 就会被替换为 `linux-x86_64`。
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
    # 这种处理方式相对比较简单粗暴，在一些实际应用场景中，可能需要根据具体情况考虑是否要给出更合适的提示信息，比如打印一条日志说明找不到对应的 `carla` 模块文件等，或者采取其他更完善的错误处理策略。
    pass

import carla

from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
    # 尝试将变量 `generation` 的值转换为整数类型，并赋值给 `int_generation` 变量。
    # 这里假设 `generation` 原本可能是字符串等其他可转换为整数的类型，通过这个转换操作以便后续基于整数类型的值进行条件判断等操作，
    # 如果 `generation` 的值无法正确转换为整数（例如它包含非数字字符等情况），就会抛出异常，进入下面的 `except` 块进行相应处理。
    int_generation = int(generation)

    # 检查转换后的整数类型的 `int_generation` 值是否在指定的可用代际列表 `[1, 2, 3]` 中。
    # 这里推测是在对某种“演员”（Actor，可能是游戏、模拟场景等中的实体对象）的代际属性进行验证，判断其是否属于合法的代际范围。
    if int_generation in [1, 2, 3]:
        # 如果 `int_generation` 的值在合法范围内（即等于1、2或3），则使用列表推导式对 `bps` 列表进行过滤筛选操作。
        # 对于 `bps` 列表中的每个元素 `x`（从命名推测 `bps` 可能是包含多个“蓝图”（Blueprint）对象的列表，这些蓝图可能用于创建演员实体），
        # 通过获取其 `'generation'` 属性并转换为整数后，与 `int_generation` 进行比较，只保留那些代际属性值与当前验证通过的 `int_generation` 值相等的元素，重新构建 `bps` 列表。
        # 最终经过筛选后的 `bps` 列表将作为结果返回，可能后续用于基于符合特定代际要求的蓝图来创建相应的演员实体。
        bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
        return bps
    else:
        # 如果 `int_generation` 的值不在 `[1, 2, 3]` 这个合法的代际范围内，说明提供的演员代际属性是无效的。
        # 此时打印一条警告信息，提示用户演员代际不合法，并且返回一个空列表，意味着不会基于当前的配置去创建任何演员实体，因为代际属性不符合要求。
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []
except:
    # 如果在前面尝试将 `generation` 转换为整数（`int(generation)` 这一行）或者后续基于代际进行列表筛选等操作过程中出现了任何异常（例如类型转换错误、属性获取错误等情况），
    # 都会进入这个 `except` 块进行异常处理。同样在这里打印一条警告信息，告知用户演员代际不合法，然后返回一个空列表，表示不会创建任何演员实体，以一种相对安全、容错的方式处理异常情况，避免程序因异常而崩溃。
    print("   Warning! Actor Generation is not valid. No actor will be spawned.")
    return []

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
        '-n', '--number-of-vehicles',
        metavar='N',
        default=30,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '-w', '--number-of-walkers',
        metavar='W',
        default=10,
        type=int,
        help='Number of walkers (default: 10)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')
    argparser.add_argument(
        '--hero',
        action='store_true',
        default=False,
        help='Set one of the vehicles as hero')
    argparser.add_argument(
        '--respawn',
        action='store_true',
        default=False,
        help='Automatically respawn dormant vehicles (only in large maps)')
    argparser.add_argument(
        '--no-rendering',
        action='store_true',
        default=False,
        help='Activate no rendering mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_list = []
    walkers_list = []
    all_id = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        world = client.get_world()

        traffic_manager = client.get_trafficmanager(args.tm_port)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        settings = world.get_settings()
        if not args.asynch:
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            else:
                synchronous_master = False
        else:
            print("You are currently in asynchronous mode. If this is a traffic simulation, \
            you could experience some issues. If it's not working correctly, switch to synchronous \
            mode by using traffic_manager.set_synchronous_mode(True)")

        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
        if not blueprints:
            raise ValueError("Couldn't find any vehicles with the specified filters")
        blueprintsWalkers = get_actor_blueprints(world, args.filterw, args.generationw)
        if not blueprintsWalkers:
            raise ValueError("Couldn't find any walkers with the specified filters")

        if args.safe:
            blueprints = [x for x in blueprints if x.get_attribute('base_type') == 'car']

        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------
        batch = []
        hero = args.hero
        for n, transform in enumerate(spawn_points):
            if n >= args.number_of_vehicles:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            if hero:
                blueprint.set_attribute('role_name', 'hero')
                hero = False
            else:
                blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        # -------------
        # Spawn Walkers
        # -------------
        # some settings
        percentagePedestriansRunning = 0.0      # how many pedestrians will run
        percentagePedestriansCrossing = 0.0     # how many pedestrians will walk through the road
        if args.seedw:
            world.set_pedestrians_seed(args.seedw)
            random.seed(args.seedw)
        # 1. take all the random locations to spawn
        spawn_points = []
        for i in range(args.number_of_walkers):
            spawn_point = carla.Transform()
            loc = world.get_random_location_from_navigation()
            if (loc != None):
                spawn_point.location = loc
                spawn_points.append(spawn_point)
        # 2. we spawn the walker object
        batch = []
        walker_speed = []
        for spawn_point in spawn_points:
            walker_bp = random.choice(blueprintsWalkers)
            # set as not invincible
            probability = random.randint(0,100 + 1);
            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')
            if walker_bp.has_attribute('can_use_wheelchair') and probability < 11:
                walker_bp.set_attribute('use_wheelchair', 'true')
            # set the max speed
            if walker_bp.has_attribute('speed'):
                if (random.random() > percentagePedestriansRunning):
                    # walking
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                else:
                    # running
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
            else:
                print("Walker has no speed")
                walker_speed.append(0.0)
            batch.append(SpawnActor(walker_bp, spawn_point))
        results = client.apply_batch_sync(batch, True)
        walker_speed2 = []
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list.append({"id": results[i].actor_id})
                walker_speed2.append(walker_speed[i])
        walker_speed = walker_speed2
        # 3. we spawn the walker controller
        batch = []
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        for i in range(len(walkers_list)):
            batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
        results = client.apply_batch_sync(batch, True)
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list[i]["con"] = results[i].actor_id
        # 4. we put together the walkers and controllers id to get the objects from their id
        for i in range(len(walkers_list)):
            all_id.append(walkers_list[i]["con"])
            all_id.append(walkers_list[i]["id"])
        all_actors = world.get_actors(all_id)

        # wait for a tick to ensure client receives the last transform of the walkers we have just created
        if args.asynch or not synchronous_master:
            world.wait_for_tick()
        else:
            world.tick()

        # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # set how many pedestrians can cross the road
        world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
        for i in range(0, len(all_id), 2):
            # start walker
            all_actors[i].start()
            # set walk to random point
            all_actors[i].go_to_location(world.get_random_location_from_navigation())
            # max speed
            all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))

        print('spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

    finally:

        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()

        print('\ndestroying %d walkers' % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
