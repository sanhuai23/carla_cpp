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
  class_<cc::ServerSideSensor, bases<cc::Sensor>, boost::noncopyable, boost::shared_ptr<cc::ServerSideSensor>>
      ("ServerSideSensor", no_init)
    .def("listen_to_gbuffer", &SubscribeToGBuffer, (arg("gbuffer_id"), arg("callback")))
    .def("is_listening_gbuffer", &cc::ServerSideSensor::IsListeningGBuffer, (arg("gbuffer_id")))
    .def("stop_gbuffer", &cc::ServerSideSensor::StopGBuffer, (arg("gbuffer_id")))
    .def("enable_for_ros", &cc::ServerSideSensor::EnableForROS)
    .def("disable_for_ros", &cc::ServerSideSensor::DisableForROS)
    .def("is_enabled_for_ros", &cc::ServerSideSensor::IsEnabledForROS)
    .def("send", &cc::ServerSideSensor::Send, (arg("message")))
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
