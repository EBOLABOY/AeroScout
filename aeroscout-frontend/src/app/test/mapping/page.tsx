// 此测试页面已被移除，因为依赖的模拟数据文件不存在
// 如需测试数据映射功能，请在开发环境中重新创建相关的模拟数据

export default function MappingTestPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">测试页面已移除</h1>
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <h3 className="text-lg font-semibold text-yellow-800">说明</h3>
        <p className="text-yellow-800">
          此测试页面已被移除，因为依赖的模拟数据文件不存在。
          如需在开发环境中测试数据映射功能，请重新创建相关的模拟数据文件。
        </p>
      </div>
    </div>
  );
}
