"""
RBAC 权限分配模块
"""

from typing import Dict, Literal


class PermissionAssigner:
    """权限分配逻辑的抽象"""

    def __init__(self, service):
        self.service = service

    def grant(
        self,
        target_type: Literal["user", "role"],
        target: str,
        permission: str,
        mode: Literal["white", "black"] = "white",
        create_permission: bool = True,
    ) -> None:
        """
        授予权限

        Args:
            target_type: 目标类型 ("user" 或 "role")
            target: 用户名或角色名
            permission: 权限路径
            mode: white=白名单, black=黑名单
            create_permission: 权限不存在时是否自动创建
        """
        if not self.service.permission_exists(permission):
            if create_permission:
                self.service.add_permission(permission)
            else:
                raise ValueError(f"权限 {permission} 不存在")

        if target_type == "user":
            if target not in self.service._users:
                raise ValueError(f"用户 {target} 不存在")
            target_data = self.service._users[target]
        else:
            if target not in self.service._roles:
                raise ValueError(f"角色 {target} 不存在")
            target_data = self.service._roles[target]

        list_key = "whitelist" if mode == "white" else "blacklist"
        opposite_key = "blacklist" if mode == "white" else "whitelist"

        target_data[list_key].add(permission)
        target_data[opposite_key].discard(permission)  # 从相反列表移除
        self.service._clear_cache()

    def revoke(
        self,
        target_type: Literal["user", "role"],
        target: str,
        permission: str,
    ) -> None:
        """撤销权限"""
        if target_type == "user":
            if target not in self.service._users:
                raise ValueError(f"用户 {target} 不存在")
            target_data = self.service._users[target]
        else:
            if target not in self.service._roles:
                raise ValueError(f"角色 {target} 不存在")
            target_data = self.service._roles[target]

        target_data["whitelist"].discard(permission)
        target_data["blacklist"].discard(permission)
        self.service._clear_cache()
