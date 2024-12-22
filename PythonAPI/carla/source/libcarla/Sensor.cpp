// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include <carla/PythonUtil.h>
#include <carla/client/ClientSideSensor.h>
#include <carla/client/LaneInvasionSensor.h>
#include <carla/client/Sensor.h>
#include <carla/client/ServerSideSensor.h>
// 定义一个静态函数 SubscribeToStream，用于让传感器订阅流并执行回调函数
static void SubscribeToStream(carla::client::Sensor &self, boost::python::object callback) {
	// 通过 MakeCallback 函数将传入的 Python 对象转换为合适的回调函数，并调用传感器的 Listen 方法进行订阅
  self.Listen(MakeCallback(std::move(callback)));
}
// 定义一个静态函数 SubscribeToGBuffer，用于让服务器端传感器订阅图形缓冲区（GBuffer）并执行回调函数
static void SubscribeToGBuffer(
  carla::client::ServerSideSensor &self,
  uint32_t GBufferId,
  boost::python::object callback) {
  self.ListenToGBuffer(GBufferId, MakeCallback(std::move(callback)));
}
// 定义一个名为 export_sensor 的函数，用于将 C++ 中的传感器类暴露给 Python
void export_sensor() {
  using namespace boost::python;
  namespace cc = carla::client;
// 定义一个名为 Sensor 的 Python 类，继承自 cc::Actor，并设置为不可复制，使用智能指针管理
  // 使用 Boost.Python 库（从代码的语法风格及相关类和函数的使用推测）来定义一个名为 `cc::Sensor` 的 Python 可绑定类（使其能在 Python 环境中使用对应的 C++ 类功能）。
// 这个类继承自 `cc::Actor` 类，并且具备不可复制的特性（通过 `boost::noncopyable` 实现，防止类对象被意外拷贝，保证对象语义的正确性），使用 `boost::shared_ptr<cc::Sensor>` 进行智能指针管理（方便内存管理，自动处理对象的生命周期等）。
// 类在 Python 中被命名为 `"Sensor"`，`no_init` 表示不进行默认初始化（可能后续需要手动按照特定方式初始化该类的对象）。
class_<cc::Sensor, bases<cc::Actor>, boost::noncopyable, boost::shared_ptr<cc::Sensor>>("Sensor", no_init)
    // 定义一个名为 `"listen"` 的函数（在 Python 环境中可调用的接口），它对应着 `SubscribeToStream` 函数（该函数应该是实现了订阅某个流的功能，可能是传感器数据相关的流，具体功能取决于 `SubscribeToStream` 函数的实现细节），
    // 函数接收一个参数 `callback`，这个参数通常是一个回调函数（用于在特定事件发生时被调用，在这里可能是当传感器有新数据产生等情况时执行相应的逻辑）。
   .def("listen", &SubscribeToStream, (arg("callback")))
    // 定义一个名为 `"is_listening"` 的函数（Python 可调用接口），它调用 `cc::Sensor::IsListening` 成员函数来判断传感器当前是否正在监听（也就是是否处于正在接收数据、处于激活状态等，具体判断逻辑由 `cc::Sensor::IsListening` 函数内部实现决定）。
   .def("is_listening", &cc::Sensor::IsListening)
    // 定义一个名为 `"stop"` 的函数（Python 可调用接口），调用 `cc::Sensor::Stop` 成员函数来停止传感器的相关操作（比如停止数据采集、停止监听等具体行为，由 `cc::Sensor::Stop` 函数的具体实现确定）。
   .def("stop", &cc::Sensor::Stop)
    // 定义一个用于将 `cc::Sensor` 类对象转换为字符串表示形式的函数（Python 可调用接口），通过 `self_ns::str(self_ns::self)` 的方式来实现转换逻辑（具体如何转换取决于 `self_ns::str` 函数的实现，可能是输出传感器的一些关键属性等信息，方便调试或者在 Python 环境中展示对象相关内容）。
   .def(self_ns::str(self_ns::self))
  ;
// 定义一个名为 ServerSideSensor 的 Python 类，继承自 cc::Sensor，并设置为不可复制，使用智能指针管理
  // 使用 Boost.Python 库来定义一个名为 `cc::ServerSideSensor` 的 Python 可绑定类，使其能够在 Python 环境中调用对应的 C++ 类的功能。
// 该类继承自 `cc::Sensor` 类（表明它具备 `cc::Sensor` 类的一些基础特性和行为），同时具有不可复制的特性（通过 `boost::noncopyable` 来确保，防止在使用过程中出现意外拷贝导致的问题，保证对象的正确语义和内存管理），并且使用 `boost::shared_ptr<cc::ServerSideSensor>` 进行智能指针管理，便于自动处理对象的生命周期以及内存资源的分配和回收等操作。
// 在 Python 中，这个类被命名为 `"ServerSideSensor"`，`no_init` 表示该类在 Python 环境中创建对象时不进行默认初始化，可能需要后续按照特定的规则和方式手动进行初始化操作。
class_<cc::ServerSideSensor, bases<cc::Sensor>, boost::noncopyable, boost::shared_ptr<cc::ServerSideSensor>>
      ("ServerSideSensor", no_init)
    // 定义一个名为 `"listen_to_gbuffer"` 的 Python 可调用函数，它对应着 `SubscribeToGBuffer` 函数实现相关功能。
    // 这个函数接收两个参数，分别是 `gbuffer_id`（推测是图形缓冲区（Graphics Buffer）的标识符，用于区分不同的缓冲区，可能与图形渲染、图像数据处理等相关）和 `callback`（通常是一个回调函数，用于在特定事件发生时执行相应的逻辑，在这里可能是当图形缓冲区有相关数据更新或者满足一定条件时被调用），用于在 Python 环境中启动对指定图形缓冲区的监听操作（具体监听的内容和后续触发回调的情况取决于 `SubscribeToGBuffer` 函数的实现细节）。
  .def("listen_to_gbuffer", &SubscribeToGBuffer, (arg("gbuffer_id"), arg("callback")))
    // 定义一个名为 `"is_listening_gbuffer"` 的 Python 可调用函数，它调用 `cc::ServerSideSensor::IsListeningGBuffer` 成员函数来判断当前是否正在对指定的 `gbuffer_id` 对应的图形缓冲区进行监听（也就是判断是否处于接收该缓冲区相关数据、关注其状态变化等的激活状态，具体判断逻辑由 `cc::ServerSideSensor::IsListeningGBuffer` 函数内部实现决定），函数接收 `gbuffer_id` 参数用于指定要检查监听状态的具体图形缓冲区。
  .def("is_listening_gbuffer", &cc::ServerSideSensor::IsListeningGBuffer, (arg("gbuffer_id")))
    // 定义一个名为 `"stop_gbuffer"` 的 Python 可调用函数，它调用 `cc::ServerSideSensor::StopGBuffer` 成员函数来停止对指定 `gbuffer_id` 对应的图形缓冲区的相关监听操作（例如停止接收该缓冲区的数据、取消关联的回调等具体行为，由 `cc::ServerSideSensor::StopGBuffer` 函数的内部实现确定），函数接收 `gbuffer_id` 参数用于明确要停止监听的具体图形缓冲区。
  .def("stop_gbuffer", &cc::ServerSideSensor::StopGBuffer, (arg("gbuffer_id")))
    // 定义一个名为 `"enable_for_ros"` 的 Python 可调用函数，调用 `cc::ServerSideSensor::EnableForROS` 成员函数来启用该传感器对于 ROS（Robot Operating System，机器人操作系统）相关功能的支持（具体启用后涉及的 ROS 相关操作和交互功能取决于 `cc::ServerSideSensor::EnableForROS` 函数的实现细节，可能涉及与 ROS 中的节点、话题等进行交互，以实现传感器数据在 ROS 环境中的传递和处理等）。
  .def("enable_for_ros", &cc::ServerSideSensor::EnableForROS)
    // 定义一个名为 `"disable_for_ros"` 的 Python 可调用函数，调用 `cc::ServerSideSensor::DisableForROS` 成员函数来禁用该传感器针对 ROS 相关功能的支持（与 `enable_for_ros` 函数相对应，执行后会停止传感器与 ROS 相关的交互等操作，具体行为由 `cc::ServerSideSensor::DisableForROS` 函数实现决定）。
  .def("disable_for_ros", &cc::ServerSideSensor::DisableForROS)
    // 定义一个名为 `"is_enabled_for_ros"` 的 Python 可调用函数，调用 `cc::ServerSideSensor::IsEnabledForROS` 成员函数来判断该传感器当前是否已经启用了针对 ROS 的相关功能支持（具体判断逻辑由 `cc::ServerSideSensor::IsEnabledForROS` 函数内部实现确定）。
  .def("is_enabled_for_ros", &cc::ServerSideSensor::IsEnabledForROS)
    // 定义一个名为 `"send"` 的 Python 可调用函数，调用 `cc::ServerSideSensor::Send` 成员函数来发送消息（推测是发送传感器相关的数据或者控制指令等信息，具体发送的内容和发送的目标等情况取决于 `cc::ServerSideSensor::Send` 函数的实现细节），函数接收 `message` 参数用于指定要发送的具体内容。
  .def("send", &cc::ServerSideSensor::Send, (arg("message")))
    // 定义一个用于将 `cc::ServerSideSensor` 类对象转换为字符串表示形式的 Python 可调用函数，通过 `self_ns::str(self_ns::self)` 的方式来实现转换逻辑（具体如何将对象转换为字符串，例如输出传感器的关键属性、当前状态等信息，取决于 `self_ns::str` 函数的实现，方便在 Python 环境中进行调试或者展示对象相关内容）。
  .def(self_ns::str(self_ns::self))
  ;
// 定义一个名为 ClientSideSensor 的 Python 类，继承自 cc::Sensor，并设置为不可复制，使用智能指针管理
  class_<cc::ClientSideSensor, bases<cc::Sensor>, boost::noncopyable, boost::shared_ptr<cc::ClientSideSensor>>
      ("ClientSideSensor", no_init)
	  // 定义一个名为 __str__ 的方法，用于在 Python 中打印客户端传感器对象时调用
    .def(self_ns::str(self_ns::self))
  ;
// 定义一个名为 LaneInvasionSensor 的 Python 类，继承自 cc::ClientSideSensor，并设置为不可复制，使用智能指针管理
  class_<cc::LaneInvasionSensor, bases<cc::ClientSideSensor>, boost::noncopyable, boost::shared_ptr<cc::LaneInvasionSensor>>
      ("LaneInvasionSensor", no_init)
	  // 定义一个名为 __str__ 的方法，用于在 Python 中打印车道入侵传感器对象时调用
    .def(self_ns::str(self_ns::self))
  ;

}
