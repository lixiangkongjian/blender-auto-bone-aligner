# 自动对齐骨骼相对位置 (Auto Bone Aligner)

Blender 插件 - 游戏装备骨骼偏移全自动烘焙工具。

## 适用场景

在游戏开发（Unreal Engine / Unity）中，角色拆卸下来的独立部件（如武器、肩甲、头盔）需要挂载到角色的骨骼（Socket/Bone）上。

为了避免在游戏引擎中手动调整旋转和位移，本插件提供一键计算并烘焙网格物体相对于目标骨骼的局部空间偏移量，使物体重置为原点状态，直接导出即可完美匹配引擎骨骼。

## 兼容性

- **Blender 3.6 LTS** 及以上版本（含 4.x）

## 安装方法

1. 下载本仓库的 `__init__.py` 文件
2. 打开 Blender → **编辑 (Edit)** → **偏好设置 (Preferences)**
3. 选择 **插件 (Add-ons)** 标签页
4. 点击右上角 **安装 (Install)** 按钮
5. 选择下载的 `__init__.py` 文件
6. 在插件列表中找到 **Auto Bone Aligner**，勾选启用

## 使用方法

1. 在 3D 视图中按 **N 键** 打开右侧边栏
2. 找到 **Game Export** 标签页
3. 在 **Bone Aligner** 面板中：
   - 选择目标网格物体（Target Mesh）
   - 选择目标骨架（Target Armature）
   - 选择目标骨骼（Target Bone）
4. 点击 **Bake Offset to Origin** 按钮

## 工作原理

基于 `mathutils.Matrix` 纯数学计算：

1. 将网格原点移动到骨骼的世界空间位置
2. 计算网格相对于骨骼的局部坐标矩阵
3. 应用反向偏移并冻结变换
4. 恢复最顶层父级缩放（兼容 UE 导出的模型缩放）

## 许可证

MIT License
