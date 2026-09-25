def calculate_postal_schemes(package_weight, total_weight):
    """
    计算邮寄方案的数量和详细信息。

    参数:
        package_weight (float): 每包莲子的重量（千克）。
        total_weight (float): 需要邮寄的总重量（千克）。

    返回:
        tuple: (方案数量, 方案详细信息列表)
    """
    # 检查总重量是否是单包重量的整数倍
    if total_weight % package_weight != 0:
        return (0, [])
    
    total_packages = int(total_weight / package_weight)
    schemes = []
    
    def partition(n, max_num, path):
        if n == 0:
            schemes.append(path.copy())
            return
        for i in range(min(max_num, n), 0, -1):
            path.append(i)
            partition(n - i, i, path)
            path.pop()
    
    partition(total_packages, total_packages, [])
    
    # 将方案转换为邮寄次数的描述
    detailed_schemes = []
    for scheme in schemes:
        detailed_schemes.append({
            'times': len(scheme),
            'details': [f"{num}包（{num * package_weight}千克）" for num in scheme]
        })
    
    return (len(schemes), detailed_schemes)

# 示例使用
package_weight = 0.25  # 每包0.25千克
total_weight = 25      # 总共25千克

count, details = calculate_postal_schemes(package_weight, total_weight)
print(f"共有 {count} 种邮寄方案：")
for i, scheme in enumerate(details, 1):
    print(f"方案 {i}: 分 {scheme['times']} 次邮寄，每次邮寄：{', '.join(scheme['details'])}")