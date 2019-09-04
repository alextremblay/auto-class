Anatomy of a data class definition:
===================================

Here is a breakdown of all the factors and variations we need to be able to handle

Every class has a header, like so:
```python
@dataclass
class {name}:
```

Every class has a body, which contains members and methods. We don't support methods yet

Members:
--------

a member definition consists of the following components:
```python
    {attribute}: {type_definition} = {expression}
```

A data class's list of members cannot contain duplicate names (ie. it should behave like a python `set`):
```python
@dataclass
class MyClass: # Not acceptable
    member: int
    member: str

@dataclass
class MyClass: # Correct
    member1: int
    member2: str
```

A member's type definition can contain multiple types:
```python
    member1: str
    member2: Union[str, int]
    member3: Optional[str]  # equivalent to Union[str, None]
    member4: Optional[Union[str, int]]
```

A member's type definition can contain types which contain types:
```python
    member1: List[str, int]
    member2: Dict[str, str]
```

Types which contain types can also contain types which contain types:
```python
    member1: List[str, List[int]]
    member2: Dict[str, Union[str,int]]
```

This library requires that all fields have a default value, so that nested dataclasses can be initialized and
iteratively constructed. Therefore, all member expressions must contain some kind of default value. If a member 
actually has a default value, this is straightforward:
```python
    member1: str = 'hello'
    member2: str = field(default='hello')
```

If a member does not have a default value, its expression must contain a default_factory for its type:
```python
    member1: str  # Not acceptable
    member2: int  # not acceptable
    member3: str = field(default_factory=str)
    member4: int = field(default_factory=int)
```

If a member is `Optional`, its default value will be `None`:
```python
    member1: Optional[str] = None
    member2: Optional[str] = field(default=None)
```

When a default value is mutable, it must be expressed as a default_factory.
```python
    member1: List[str] = []  # Not acceptable
    member2: List[str] = ['hello']  # Not supported
    member3: List[str] = field(default_factory=list)  # Correct
```

A member can be optional and have no specific type.
```python
    member: Any = None
```

A member can also have metadata related to controlling marhmallow behavior for that member. If a member has any such 
metadata, its expression must be represented as a `field` definition with metadata:
```python
    member1: str = 'hello'  # Not acceptable, metadata not captured
    member2: str = field(default='hello', metadata=dict({metadata}))  # Correct
    member3: List[str] = field(default_factory=list, metadata=dict({metadata}))  # Correct
```

A member can have a name which is not a valid python attribute name. When this happens, a valid python attribute name 
must be derived from the member name, and the actual member name must be added to the member's metadata mapping under
the 'data_key' key:
```python
    Member Name: str = 'hello'  # Not acceptable
    member_name: str = field(default='hello', metadata=dict(data_key='Member Name')) # Correct
```

Members has a number of properties which affect how marshmallow handles them, such as:

 - Optional: a member can be treated as optional by marshmallow:
   ```python
       member1: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False))
       member2: str = field(default_factory=str, metadata=dict(default=str, missing=str, required=False))
   ```
 - Custom Field: a member can have a custom marshmallow field (instead of the default field inferred for that member 
   by the `marshmallow_dataclass` library the we leverage):
   ```python
       member: str = field(default='email@address.com', metadata=dict(marshmallow_field=Email))
   ```