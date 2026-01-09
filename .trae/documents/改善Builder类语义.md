基于对代码库的分析，我建议将Builder类重命名为FrameFactory，以改善语义并使调用更加自然。以下是具体方案：

1. **重命名原因**：

   * 当前Builder类不符合传统Builder模式（没有build()方法）

   * 它实际上是一个工厂类，用于创建不同类型的Frame对象

   * FrameFactory名称更符合其实际功能，语义更清晰

2. **修改范围**：

   * 修改所有厂商的builder.py文件，将Builder类重命名为FrameFactory

   * 更新所有导入语句和使用处

   * 保持类方法不变，只修改类名

3. **预期效果**：

   * 调用方式更自然：`FrameFactory.get_play_item()` 清晰表示"获取一个播放项的Frame对象"

   * 符合工厂模式的命名惯例

   * 保持代码结构不变，易于维护和扩展

   * 所有厂商SDK保持统一命名

4. **实施步骤**：

   * 重命名所有builder.py文件中的Builder类为FrameFactory

   * 更新所有protocol.py文件中的导入和使用

   * 更新其他可能的使用处

   * 验证修改后的代码语法正确性

5. **示例修改**：

   ```python
   # 原代码
   from .builder import Builder
   self.send(bytes(Builder.get_play_item()))

   # 修改后
   from .builder import FrameFactory
   self.send(bytes(FrameFactory.get_play_item()))
   ```

