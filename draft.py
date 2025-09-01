import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# 数据
data_sets = {
    "set1": [1.255, 1.255, 1.254, 1.256, 1.255],
    "set2": [3.022, 3.018, 3.020, 3.018, 3.018],
    "set3": [6.048, 6.045, 6.048, 6.031, 6.043]
}

# 创建图形
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# 绘制每组数据的高斯分布图
for i, (key, data) in enumerate(data_sets.items()):
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)

    # 创建x值，使用对数范围
    x = np.logspace(np.log10(mean - 4*std_dev), np.log10(mean + 4*std_dev), 100)

    # 计算高斯分布的y值
    y = stats.norm.pdf(x, mean, std_dev)

    # 绘制高斯分布曲线
    axs[i].plot(x, y, label=f'{key} (Mean: {mean:.4f}, Std Dev: {std_dev:.4f})')

    # 设置图形属性
    axs[i].set_xscale('log')  # 设置x轴为对数刻度
    axs[i].set_title(f'Gaussian Distribution of {key}')
    axs[i].set_ylabel('Probability Density')
    axs[i].grid()

    # 只在最后一个子图显示x轴标签
    if i < len(data_sets) - 1:
        axs[i].set_xticklabels([])  # 隐藏x轴标签

# 设置共享的x轴标签
plt.xlabel('Value (Log Scale)')
plt.tight_layout()
plt.show()