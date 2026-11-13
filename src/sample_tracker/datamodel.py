from enum import Enum
from odmantic import (
    Model,
    Field,
)
from bson import ObjectId
from pydantic import (
    EmailStr,
    model_validator,
)
from typing import (
    Any, Optional,
)
import hashlib
from pathlib import Path
from markdown import markdown
from justhtml import JustHTML
from datetime import datetime
from sample_tracker.utility import (
    human_readable_filesize,
    naive_utc_timestamp,
)
class EnumExtra():
    """
    Adds simple names & values methods to a Enum class to make it easy
    to get sets of the available entries in the Enum
    """
    @classmethod
    def names(cls):
        return {x.name for x in cls}
        
    @classmethod
    def values(cls):
        return {x.value for x in cls}
    

class ProjectStatus(EnumExtra, str, Enum):
    proposed = "Proposed"
    active = "Active"
    completed = "Completed"

    def get_colour_class(self):
        colour_class_map = {
            # "Proposed": "warning-emphasis",
            "Proposed": "warning",
            "Active": "success",
            "Completed": "secondary",
        }
        return colour_class_map.get(self.value)

class ApprovalStatus(EnumExtra, str, Enum):
    notsubmitted = "Not Submitted"
    approved = "Approved"
    revise = "Requires Revisions"
    pending = "Pending"
    denied = "Denied"

    def get_colour_class(self):
        colour_class_map = {
            "Not Submitted": "secondary",
            "Approved": "success",
            "Requires Revisions": "warning",
            "Pending": "info",
            "Denied": "danger",
        }
        return colour_class_map.get(self.value)

# class Roles(str, Enum):
class Authorizations(EnumExtra, str, Enum):
    move = "Move"
    view = "View"
    edit = "Edit"
    admin = "Admin"

    def get_colour_class(self):
        colour_class_map = {
            "Move": "primary",
            "View": "info",
            "Edit": "warning",
            "Admin": "danger",
        }
        return colour_class_map.get(self.value)

class Restriction(EnumExtra, str, Enum):
    """
    Args:
        title (str):
        description: (str | None): 
        date_created (datetime):
        status (ProjectStatus):
        restrictions (set[ObjectId] | None):
        samples (set[ObjectId] | None): 
        attachments (set[ObjectId] | None):
        
    """
    title: str
    description: str = "" # None
    date_created: datetime = Field(default_factory = naive_utc_timestamp)
    status: ProjectStatus = Field(default = ProjectStatus.proposed)
    restrictions: list[ObjectId] | None = None # Restriction
    restriction_details: dict = {}
    samples: list[ObjectId] = [] #| None = None
    attachments: list[ObjectId] = [] # File
    tags: dict[str,str] = {} # use set
    owner: ObjectId # Id of person, the creator by default
    # authorisatons: dict[str, set[ObjectId]] # permission name and a set of those who have it.
    authorizations: dict[str, dict[str, int]] # permission name and a set of those who have it.
    # authorizations: dict[ObjectId, dict[Authorizations, int]] # permission name and a set of those who have it.
    def get_tags(self):
        return {k for k in self.tags.keys()}

    def get_description_html(self):
        project_description_raw = markdown(self.description)
        return JustHTML(project_description_raw, fragment = True).to_html(pretty=False)


class Role(EnumExtra, str, Enum):
    create = "Create"
    admin = "Admin"
    approve_hta = "HTA"
    approve_radioactivity = "Radiation"
    approve_bsl2 = "BSL-2"

    def get_colour_class(self):
        colour_class_map = {
            "Create": "warning",
            "Admin": "danger",
            "HTA": "info",
            "Radiation": "info",
            "BSL-2": "info",
        }
        return colour_class_map.get(self.value)

    
class Person(Model):
    """
    :Args:
        username (str):
        given_name (str):
        family_name (str):
        email (str):

    :Example:
        >>> ex_person = Person(username = "test", given_name = "test", family_name = "testington", email = "test@example.com")
        >>> ex_person.username
        'test'
    """
    username: str
    given_name: str
    family_name: str
    email: EmailStr
    email_verified: bool = Field(default = False)
    disabled: bool = Field(default = False)
    last_authenticated: datetime | None = None
    date_created: datetime = Field(default_factory = naive_utc_timestamp)
    roles: dict[Role,int] = {} # set()
    # can_approve: set[str] | None = None # Resctiction Names
    
    def get_roles(self):
        return {k.value for k in self.roles.keys()}
    
    def get_roles_csl(self):
        return ", ".join(self.roles.keys())

class Team(Model):
    members: set[ObjectId] # ObjectId str & usernames?

class EventTypes(EnumExtra, str, Enum):
    arrived = "Arrived"
    moved = "Moved"
    destroyed = "Destroyed"
    removed = "Removed"

class Event(Model):
    samples: set[ObjectId] # Sample
    person: ObjectId
    time: datetime = Field(default_factory = naive_utc_timestamp)
    type: EventTypes
    process: str
    
class Sample(Model):
    name: str
    description: str
    location: str
    restrictions: set[ObjectId]

class SampleGroup(Model):
    samples: set[ObjectId] # Sample

class Building(str, Enum):
    example = "Example Building"
    
class Room(str, Enum):
    example = "Example Room"
    
class Location(Model):
    building: Building
    room: Room
    container: str
    restrictions_suitable_for: set[ObjectId]

# class Authorization(Model):
#     person: ObjectId  # Person
#     project: ObjectId # Project
#     roles: set[Roles]

class File(Model):
    path: str # Path
    size: int | None = None # bytes
    hash: str | None = None
    hashalgo: str = Field(default = "sha256") # defined list from hashlib?
    
    def get_filename(self):
        return Path(self.path).name

    def get_human_size(self):
        return human_readable_filesize(self.size)

    @model_validator(mode="before")
    @classmethod
    def get_hash(cls, instance):
        hash = instance.get("hash")
        try:
            algo_name = cls.model_fields["hashalgo"].default
            if instance.get("hashalgo") is not None:
                algo_name = instance.get("hashalgo")
            algo = hashlib.new(algo_name)
            with open(instance.get("path"), "rb") as f:
                algo.update(f.read())
            computed_hash = algo.hexdigest()
        except Exception as e:
            raise ValueError(f"{e}")
        if hash is None:
            instance["hash"] = computed_hash
            return instance
        else:
            if hash != computed_hash:
                raise Exception(f"Supplied hash {hash} does not match computed {computed_hash}")
        return instance
        
    @model_validator(mode="before")
    @classmethod
    def get_filesize(cls, instance):
        size = instance.get("size")
        try:
            comp_size = Path(instance.get("path")).stat().st_size
        except Exception as e:
            raise ValueError(f"Error computing file size {e}")
        if size is None:
            instance["size"] = comp_size
            return instance
        else:
            comp_size = Path(instance.get("path")).stat().st_size
            if instance["size"] != comp_size:
                raise Exception(f"Provided file size of {instance.size} is not equal to size of file at the provided path {comp_size}")
        return instance
