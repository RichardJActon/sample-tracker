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
from datetime import (
    datetime,
    timezone,
)

def naive_utc_timestamp():
    """
    MongoDb only supports naive timestamps recorded in UTC but does not
    explicitly store this timezone information.
    """
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)

class ProjectStatus(str, Enum):
    proposed = "Proposed"
    active = "Active"
    completed = "Completed"

class Project(Model):
    title: str
    description: str
    date_created: datetime = Field(default_factory = naive_utc_timestamp)
    status: ProjectStatus = Field(default = ProjectStatus.proposed)
    restrictions: set[ObjectId] | None # = []
    samples: set[ObjectId] | None
    attachments: set[ObjectId] | None # File
    
class Person(Model):
    username: str
    given_name: str
    family_name: str
    email: EmailStr
    email_verified: bool = Field(default = False)
    disabled: bool = Field(default = False)
    last_authenticated: datetime | None = None
    date_created: datetime = Field(default_factory = naive_utc_timestamp)

class Team(Model):
    members: set[ObjectId] # ObjectId str & usernames?

class EventTypes(str, Enum):
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
    
class Restriction(Model):
    name: str
    description: str
    requirements: dict[str,Any] = Field(default = dict())
    
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

class ApprovalStatus(str, Enum):
    approved = "Approved"
    pending = "Pending"
    denied = "Denied"
    
class Roles(str, Enum):
    mover = "Move"
    viewer = "View"
    approve_hta = "Approve HTA"
    approve_radioactivity = "Radioactivity"
    approve_cat2 = "Approve Cat2"

class Authorization(Model):
    person: ObjectId  # Person
    project: ObjectId # Project
    roles: set[Roles]

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

