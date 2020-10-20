from peewee import *
import datetime
from passlib.context import CryptContext
import re
from utils.ClientModels import database_proxy
import logging

# database_proxy = Proxy()

logger = logging.getLogger(__name__)

# re
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")

# Setting up passlib.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", ],
    default="pbkdf2_sha256",
    all__vary_rounds=0.1,
    pbkdf2_sha256__default_rounds=20000,
)

class MyBaseModel(Model):
    """
    实现一个新的基类，Model是peewee的基类;
    新增get_or_none()接口，封装peewee的get()接口，
    查询不到返回None，而不抛出异常。
    """
    class Meta:
        database = database_proxy

    is_valid = BooleanField(default=True)
    created = TimestampField()
    modified = TimestampField()
    revision = IntegerField(default=0)

    @classmethod
    def get_or_none(cls, *args, **kwargs):
        try:
            return cls.get(*args, **kwargs)
        except DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        self.revision += 1
        super(MyBaseModel, self).save(*args, **kwargs)



class User(MyBaseModel):
    username = CharField(unique=True)
    name = CharField(default='')
    password = CharField(default='')

    class Meta:
        order_by = ('username',)

    def crypt_password(self, password):
        """
        加密
        :param password:
        :return: cls.password
        """
        self.password = pwd_context.encrypt(password)
        return self.password

    def verify_password(self, password):
        """
        验证密码
        :param password:
        :return: True/False
        """
        return pwd_context.verify(password, self.password)

    @classmethod
    def username_valid(cls, username):
        """
        用户名格式
        :param username:
        :return: True/False
        """
        if USER_RE.match(username):
            return True
        else:
            return False

    @classmethod
    def password_valid(cls, password):
        """
        密码格式
        :param password:
        :return: True/False
        """
        if PASS_RE.match(password):
            if len(password) < 5 or len(password) > 14:
                return False
            else:
                return True
        else:
            return False

    @classmethod
    def create_user(cls, username, password, **kwargs):
        """
        新建用户
        :param username:
        :param password:
        :param kwargs:
        :return: User object
        """
        if User.username_valid(username=username):
            # 用户名格式
            encrypted_username = username
        else:
            return False
        if User.password_valid(password=password):
            # 密码格式，且长度大于等于6小于等于14
            encrypted_password = pwd_context.encrypt(password)
        else:
            return False
        return User.create(username=encrypted_username, password=encrypted_password, **kwargs)

    @classmethod
    def get_user(cls, user_id):
        """
        根据user_id获取用户
        :param user_id:
        :return: User object
        """
        return cls.get_or_none(cls.id == user_id)

    @classmethod
    def get_user_by_username(cls, username):
        """
        :return: User object
        """
        return cls.get_or_none(cls.username == username)

    def assign_group(self, group_id):
        """
        给用户分配组
        :param group_id:
        :return: UserGroup object
        """
        return UserGroup.add_user_to_group(user_id=self.id, group_id=group_id)

    def change_password(self, old_password, new_password):
        """
        修改密码
        :param old_password:
        :param new_password:
        :return: 修改成功后保存返回 True,否则返回 False
        """
        # invalid format of old password is considered invalid to save processing
        if User.password_valid(old_password):
            if not self.verify_password(old_password):
                return False
            # verify new password, format and length
            if User.password_valid(new_password):
                if old_password == new_password:
                    return False
                else:
                    self.password = self.crypt_password(password=new_password)
                    self.save()
                    return True
        return False


class Operation(MyBaseModel):
    """
    操作表
    """
    key = CharField(unique=True)
    name = CharField(default='')
    parent_key = CharField(default='')
    detail = CharField(default='')
    level = IntegerField(default=0)
    sort = IntegerField(default=0)

    @classmethod
    def get_operation(cls,name):
        return cls.get_or_none(cls.name == name)

    @classmethod
    def get_operation_id(cls,key):
        return cls.get(cls.key == key).id

    @classmethod
    def create_operation(cls, key, **kwargs):
        """
        新加操作
        :param key:
        :param kwargs:
        :return: key/Operation object
        """
        operation = cls.get_or_none(cls.key == key)
        if operation:
            return operation.key
        else:
            return cls.create(key=key, **kwargs)

    def assign_group(self, group_id):
        """
        给操作分配组
        :param group_id:
        :return: GroupOperatePermission object
        """
        return GroupOperatePermission.add_operation_to_group(operation_id=self.id, group_id=group_id)


class Group(MyBaseModel):
    name = CharField(unique=True)
    detail = CharField(default='')


    @classmethod
    def create_group(cls, name, **kwargs):
        """
        新建组
        :param name:
        :return: name/Group object
        """
        group = cls.get_or_none(cls.name == name)
        if group:
            return group.name
        else:
            return cls.create(name=name, **kwargs)

    @classmethod
    def get_group(cls, group_id):
        """
        根据group_id获取组
        :param group_id:
        :return: Group object/None
        """
        return cls.get_or_none(cls.id == group_id)

    def add_user(self, user_id):
        """
        组中添加用户
        :param user_id:
        :return: UserGroup object
        """
        return UserGroup.add_user_to_group(user_id=user_id, group_id=self.id)

    def add_operation(self, operation_id):
        """
        组中添加操作
        :param operation_id:
        :return: GroupOperatePermission object
        """
        return GroupOperatePermission.add_operation_to_group(operation_id=operation_id, group_id=self.id)


class UserGroup(MyBaseModel):
    """
    用户组表
    """

    class Meta:
        primary_key = CompositeKey('user', 'group')

    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)

    @classmethod
    def get_ug_by_group_id(cls, group_id):
        """
        根据group_id获取用户组
        :param group_id:
        :return: UserGroup SelectQuery
        """
        return cls.select(UserGroup, Group).join(Group).where(cls.group == group_id)

    @classmethod
    def get_ug_by_user_id(cls, user_id):
        """
        根据user_id获取用户组
        :param user_id:
        :return: UserGroup SelectQuery
        """
        return cls.select(UserGroup, User).join(User).where(cls.user == user_id)

    @classmethod
    def add_user_to_group(cls, user_id, group_id):
        """
        添加用户到组里
        :param user_id:
        :param group_id:
        :return:  UserGroup object
        """
        if cls.user_is_a_member_of_group(user_id=user_id, group_id=group_id):
            return False
        else:
            return cls.create(user=user_id, group=group_id)

    @classmethod
    def delete_user_from_group(cls, user_id, group_id):
        """
        从组里删除用户
        :param user_id:
        :param group_id:
        :return:  None
        """
        try:
            ug = cls.get(cls.user == user_id, cls.group == group_id)
            return ug.delete_instance()
        except UserGroup.DoesNotExist:
            return False

    @classmethod
    def user_is_a_member_of_group(cls, user_id, group_id):
        """
        用户是否是组的成员
        :param user_id:
        :param group_id:
        :return: True/False
        """
        query = cls.select().where(cls.user == user_id, cls.group == group_id)
        if len(query) == 0:
            return False
        elif len(query) == 1:
            return True
        else:
            return False

    @classmethod
    def get_groups_of_user(cls, user_id):
        """
        获取用户所属的所有组
        :param user_id:
        :return: lists
        """
        lists = []
        ugs = cls.get_ug_by_user_id(user_id=user_id)
        for ug in ugs:
            lists.append(ug.group.name)
        return lists

    @classmethod
    def get_users_in_group(cls, group_id):
        """
        获取组中所有的用户
        :param group_id:
        :return:  lists
        """
        lists = []
        ugs = cls.get_ug_by_group_id(group_id=group_id)
        for ug in ugs:
            lists.append(ug.user.username)
        return lists


class GroupOperatePermission(MyBaseModel):
    """
    授权表
    """

    class Meta:
        primary_key = CompositeKey('group', 'operation')

    group = ForeignKeyField(Group)
    operation = ForeignKeyField(Operation)

    @classmethod
    def get_gop_by_group_id(cls, group_id):
        """
        根据group_id获取授权表
        :param group_id:
        :return: GroupOperatePermission SelectQuery
        """
        return cls.select(GroupOperatePermission, Group).join(Group).where(cls.group == group_id)

    @classmethod
    def get_gop_by_operation_id(cls, operation_id):
        """
        根据operation_id获取授权表
        :param operation_id:
        :return: GroupOperatePermission SelectQuery
        """
        return cls.select(GroupOperatePermission, Operation).join(Operation).where(cls.operation == operation_id)

    @classmethod
    def add_operation_to_group(cls, operation_id, group_id):
        """
        增加操作到组
        :param operation_id:
        :param group_id:
        :return: GroupOperatePermission object
        """
        if cls.operation_is_a_member_of_group(operation_id=operation_id, group_id=group_id):
            return False
        else:
            return cls.create(operation=operation_id, group=group_id)

    @classmethod
    def delete_operation_from_group(cls, operation_id, group_id):
        """
        从组中删除操作
        :param operation_id:
        :param group_id:
        :return: None/False
        """
        try:
            gop = cls.get(cls.operation == operation_id, cls.group == group_id)
            return gop.delete_instance()
        except GroupOperatePermission.DoesNotExist:
            return False

    @classmethod
    def operation_is_a_member_of_group(cls, operation_id, group_id):
        """
        判断成员
        :param operation_id:
        :param group_id:
        :return: True/False
        """
        query = cls.select().where(cls.operation == operation_id, cls.group == group_id)
        if len(query) == 0:
            return False
        elif len(query) == 1:
            return True
        else:
            return False

    @classmethod
    def get_groups_with_operation(cls, operation_id):
        """
        获取拥有某个操作的所有组
        :param operation_id:
        :return: lists
        """
        lists = []
        gops = cls.get_gop_by_operation_id(operation_id=operation_id)
        for gop in gops:
            lists.append(gop.group.name)
        return lists

    @classmethod
    def get_operations_of_group(cls, group_id):
        """
        获取某一个组中所有的操作
        :param group_id:
        :return: lists
        """
        lists = []
        gops = cls.get_gop_by_group_id(group_id=group_id)
        for gop in gops:
            lists.append(gop.operation.name)
        return lists

def getPermission(userName):
    # 根据用户名获取权限
    try:
        userId = User.get_user_by_username(userName).id
        groupId = UserGroup.get_ug_by_user_id(userId)[0].group
        permissionList = GroupOperatePermission.get_operations_of_group(groupId)
    except:
        return None
    return permissionList