from bson import ObjectId
from typing import (
    Dict,
    List,
    Callable,
    TypeAlias,
)
from enum import Enum
from dataclasses import (
    dataclass,
)
from functools import (
    partial,
    # reduce,
)
from sample_tracker.datamodel import (
    Person,
    Role,
)

def can_change_project_ownership(person, project):
    # may also want current project owners to
    # be able to change project ownership
    # even if they are not admins?
    if Role.admin in person.roles.keys():
        return True
    elif "edit" in (project.authorizations.get(str(person.id)) or []):
        return True
    else:
        return False
        # raise Exception("cannot change project ownership")

def can_person_edit_project(person, project):
    if "edit" in (project.authorizations.get(str(person.id))or []):
        return True
    elif project.owner == person.id:
        # NB owners should also be in authorizations, included defensively
        return True
    else:
        return False
        # raise PermissionError(
        #     # f"{person.username} ({str(person.id)}) cannot view Project {project.title} ({str(project.id)})"
        #     f"{person.username} ({str(person.id)}) cannot view Project ({str(project.id)})"
        # )

def can_person_see_project(person, project):
    if "view" in (project.authorizations.get(str(person.id)) or []):
        return True
    elif project.owner == person.id:
        # NB owners should also be in authorizations, included defensively
        return True
    else:
        return False
        # raise PermissionError(
        #     # f"{person.username} ({str(person.id)}) cannot view Project {project.title} ({str(project.id)})"
        #     f"{person.username} ({str(person.id)}) cannot view Project ({str(project.id)})"
        # )

def can_person_create_project(person):
    # person only input make method?
    if Role.create in person.roles.keys():
        return True
    elif Role.admin in person.roles.keys():
        return True
    else:
        return False
        # raise PermissionError(
        #     f"{person.username} cannot create new projects"
        # )

def get_current_person(engine, session):
    return engine.find_one(
        Person, Person.username == session["user"]["preferred_username"]
    )

def is_admin(person):
    if Role.admin in person.roles.keys():
        return True
    else:
        return False
    

# Permissions ----
# class Permissions(str, Enum):
#     view = "view"
#     move = "move"
#     # approve_hta = "Approve HTA"
#     admin = "admin"
    
# UserPermissions: TypeAlias = dict[str, list[Permissions]]
# # ProjectPermissions: TypeAlias = dict[str, set[ObjectId]]
# # ProjectPermissions: TypeAlias = dict[Permissions, set[ObjectId]]
# PolicyFn: TypeAlias = Callable[[UserPermissions, Permissions], UserPermissions]

# # def check_project_permission(person, project):# permissions):
# #     # if person in permissions:
# #     if person in project.authorization:
# #         return person
# #     else:
# #         raise PermissionError(f"{str(person)} does not have {str()}")

# def check_permission(member: UserPermissions, permission: Permissions) -> UserPermissions:
#     if permission not in next(iter(member.values())):
#         raise PermissionError(f"{next(iter(member))} does not have {str(permission.value)} permissions")
#     return member

# # permissions_checkers
# for v in [e for e in Permissions]:
#     # alternatively make a dict (maybe an enum would be better?) of functions which can be called
#     # permissions_checkers[v.value] = partial(check_permission, permission = v)
    
#     # programatically generate the check_perm_x functions from the list of permissions
#     # and place them in the global namespace for this module
#     # (NB this does seem to upset the static analysis which can't find the function declatations so complains about using undeclared objects)
#     globals()['check_perm_%s' % v.value] = partial(check_permission, permission = v)

# # check_project_member(person, project):
# #     person.id in [... project.authorzations]

# # policies = [check_perm_view, check_perm_move]

# def apply_permissions(user: UserPermissions, policies: List[PolicyFn]) -> UserPermissions:
#     # return reduce(lambda policy, user: policy(user), policies, user)
#     for p in policies:
#         p(user)
#     return user

# def apply_project_permissions(person, project):
#     project.authorizations[person.id]

