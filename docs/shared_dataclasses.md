# Why don't we support shared dataclasses?

> Note: This page is very implementation-focused. references to 'we' in this document refer to the project maintainers 
and any good samaritan looking to contribute to the project

## What are shared dataclasses?
It is entirely possible for a data structure to contain multiple objects in different parts of the tree which represent 
the same thing. Currently, it's not possible to model this relationship.

ex:
```yaml
MyDataClass:
    shared_object:
        field_a: ''
        field_b: 0
        field_c: False
    nested_object:
        shared_object:
            field_a: ''
            field_b: 0
            field_c: False
```
logically, these two `shared_object` objects are the same. in an ideal world, when serializing this nested object into 
dataclass instances, these two would both be instances of a single `SharedObject` dataclass. In reality, when using 
this tool to generate a dataclass loader (aka a deserializer) for this data structure, that loader will convert these 
objects into instances of `Dataclass.SharedObject` and `Dataclass.NestedObject.SharedObject` dataclasses respectively.

## Why don't we support them?
currently, this project, when given the above example, would generate the following dataclass definition:
```python
from marshmallow_dataclass import dataclass

@dataclass
class MyDataClass:
    
    @dataclass
    class SharedObject:
        field_a: str
        field_b: int
        field_c: bool
        
    shared_object: SharedObject
    
    @dataclass
    class NestedObject:
    
        @dataclass
        class SharedObject:
            field_a: str
            field_b: int
            field_c: bool
            
        shared_object: SharedObject
    
    nested_object: NestedObject
```

In order to support shared dataclasses, what we really want to do is generate this dataclass definition:
```python
from marshmallow_dataclass import dataclass

@dataclass
class SharedObject:
    field_a: str
    field_b: int
    field_c: bool

@dataclass
class NestedObject:            
    shared_object: SharedObject

@dataclass
class MyDataClass:        
    shared_object: SharedObject
    nested_object: NestedObject
```

That's much better, right? cleaner, flatter, less noisy, deduplicated. Much easier to visually parse, and see which 
classes have which members.

The problems that get in the way are as follows:
 - Name collisions: What if two different objects in different parts of the tree have the same name, but totally 
   different members? In a flat dataclass definition scheme like the one above, they can't both have the same name. 
   One or both of them will need to be renamed. How do we detect this condition? What kind of naming convention / 
   rename logic should we apply when this happens?
 - Partial objects: If two objects have the same name, and the same members, we should treat them as instances of the 
   same dataclass. If two objects have the same name and completely different sets of members, we should treat them as 
   different classes. But what if two objects have the same name and *almost* the same members (maybe one is a subset 
   of the other, or maybe they have 5 members in common and each has a different sixth member)? How do we handle that?
 
## What do we need to do to be able to support them?
First thing we'll need to do is set up some kind of registry to track defined dataclasses and their members. Every time 
we recurse into a new object and prepare to create a dataclass definition for it, we should first check to see if a 
dataclass with that name already exists.
If one does, we should do some kind of membership analysis to decide if this object should be treated as an instance of 
that already-defined dataclass. 

 - If it should, then set this object as a reference ot that dataclass. 

 - If it shouldn't, then we need to rename the dataclass definition for the new object (and maybe also rename the 
   dataclass definition for the old object too?). 
    1. One idea is to prefix it with the parent's dataclass name (ex: the two shared objects from the example would 
       become `MyDataClassSharedObject` and `NestedObjectSharedObject` definitions), but i don't really like this idea. 
       Looks ugly and excessively verbose. 
    2. Another idea is to suffix each dataclass with a number (ex: the two shared objects from the example would 
       become `SharedObject1` and `SharedObject2`), but i'm not really fond of this idea either. 
    3. Another option would be to fail early and prompt the user to manually add explicit dataclass `n:{name}` comment 
       tokens to the offending , instead of automatically renaming the dataclasses.
        - **pro**: each user can decide on a naming scheme that makes the most sense for their use case
        - **con**: requires manual intervention on the part of the user, which is something we should always strive to 
          minimize or eliminate. This tool is supposed to be automatic, as the name suggests
     
 - If an object SHOULD be treated as an instance of an existing dataclass definition, but doesn't have the same set of 
   members, How should we detect that?. One idea is to store ,within each data class definition in the registry, a set 
   of all its members and their types. Any time we encounter another object with the same dataclass name, we could do a 
   member-set intersection between the registered dataclass and the newly-detected dataclass, and if the number of 
   members that intersect is above a certain threshold (maybe like... 70%?), Then this will treated as an instance of 
   that existing dataclass. We can also at this point do a symmetric difference operation to get the members which 
   aren't part of both sets and mark those members with the `AllowMissing` flag. Also, we need to hadle situations 
   where a member that exists in both instances has a different type in each instance (ex. in one instance, it's a `str`, 
   in the other it's a `int`). Ideally, this condition should be detected, and the final type for that member 
   should resolve to `Union[str,int]`