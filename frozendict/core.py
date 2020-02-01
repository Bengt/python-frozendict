from copy import deepcopy

def notimplemented(self, *args, **kwargs):
    r"""
    Not implemented.
    """
    
    raise NotImplementedError(f"`{self.__class__.__name__}` object is immutable.")

class frozendict(dict):
    r"""
    A simple immutable dictionary.
    
    The API is the same as `dict`, without methods that can change the 
    immutability.
    In addition, it supports __hash__() and the operands __add__() and 
    __sub__().
    """
    
    __slots__ = (
        "initialized", 
        "_hash", 
        "is_frozendict", 
    )
    
    @classmethod
    def fromkeys(cls, *args, **kwargs):
        r"""
        Identical to dict.fromkeys().
        """
        
        return cls(dict.fromkeys(*args, **kwargs))
    
    def __new__(cls, *args, **kwargs):
        r"""
        Almost identical to dict.__new__().
        """
        
        # enable attribute setting for __init__,
        # only for the first time
        cls.__setattr__ = object.__setattr__
        
        has_kwargs = bool(kwargs)
        
        if len(args) == 1 and not has_kwargs:
            it = args[0]
            
            if isinstance(it, cls):
                it.initialized = 2
                return it
        
        use_empty = False
        
        if not has_kwargs:
            use_empty = True
            
            for arg in args:
                if arg:
                    use_empty = False
                    break
            
        if use_empty:
            try:
                self = cls.empty
                return self
            except AttributeError:
                initialized = 3
        else:
            initialized = 0
        
        self = super().__new__(cls)
        self.initialized = initialized
                
        
        return self
    
    def __init__(self, *args, **kwargs):
        r"""
        Almost identical to dict.__init__(). It can't be reinvoked.
        """
        
        if self.initialized == 2:
            self.initialized = 1
            return
        
        klass = self.__class__
        
        if self.initialized != 3 and self is klass.empty:
            return
        
        if self.initialized == 1:
            # object is immutable, can't be initialized twice
            notimplemented(self)
        
        super().__init__(*args, **kwargs)
        
        self._hash = None
        self.initialized = 1
        self.is_frozendict = True
        
        # object is created, now inhibit its mutability
        klass.__setattr__ = notimplemented
    
    def hash_no_errors(self, *args, **kwargs):
        r"""
        Calculates the hash if all values are hashable, otherwise returns -1
        """
        
        _hash = self._hash
        
        if _hash is None:
            # try to cache the hash. You have to use `object.__setattr__()`
            # because the `__setattr__` of the class is inhibited 
            hash1 = 0

            for v in self.values():
                try:
                    hash_v = v.__hash__()
                except Exception:
                    hash_res = -1
                    object.__setattr__(self, "_hash", hash_res)
                    return hash_res
                
                hash1 ^= ((hash_v ^ 89869747) ^ (hash_v << 16)) * 3644798167

            hash2 = hash1 ^ ((len(self) + 1) * 1927868237)
            hash3 = (hash2 ^ ((hash2 >> 11) ^ (hash2 >> 25))) * 69069 + 907133923

            if hash3 == -1:
                hash_res = 590923713
            else:
                hash_res = hash3
            
            object.__setattr__(self, "_hash", hash_res)
        else:
            hash_res = _hash
        
        return hash_res
    
    def __hash__(self, *args, **kwargs):
        r"""
        Calculates the hash if all values are hashable, otherwise raises a 
        TypeError.
        """
        
        _hash = self.hash_no_errors(*args, **kwargs)
        
        if _hash == -1:
            raise TypeError("Not all values are hashable.")
        
        return _hash
    
    def __repr__(self, *args, **kwargs):
        r"""
        Identical to dict.__repr__().
        """
        
        body = super().__repr__(*args, **kwargs)
        
        return f"{self.__class__.__name__}({body})"
    
    def copy(self):
        r"""
        Return the object itself, as it's an immutable.
        """
        
        return self
    
    def __copy__(self, *args, **kwargs):
        r"""
        See copy().
        """
        
        return self.copy()
    
    def __deepcopy__(self, *args, **kwargs):
        r"""
        If hashable, see copy(). Otherwise it returns a deepcopy.
        """
        
        _hash = self.hash_no_errors(*args, **kwargs)
        
        if _hash == -1:
            tmp = dict(self)
            
            for k, v in tmp.items():
                tmp[k] = deepcopy(v)
            
            return self.__class__(tmp)
        
        return self.copy()
    
    def __reduce__(self, *args, **kwargs):
        r"""
        Support for `pickle`.
        """
        
        return (self.__class__, (dict(self), ))
    
    def __add__(self, other, *args, **kwargs):
        """
        If you add a dict-like object, a new frozendict will be returned, equal 
        to the old frozendict updated with the other object.
        """
        
        tmp = dict(self)
        
        try:
            tmp.update(other)
        except Exception:
            raise TypeError(f"Unsupported operand type(s) for +: `{self.__class__.__name__}` and `{other.__class__.__name__}`") from None
        
        return self.__class__(tmp)
    
    def __sub__(self, iterable, *args, **kwargs):
        """
        You can subtract an iterable from a frozendict. A new frozendict will 
        be returned, without the keys that are in the iterable.
        """
        
        try:
            iter(iterable)
        except Exception:
            raise TypeError(f"Unsupported operand type(s) for -: `{self.__class__.__name__}` and `{iterable.__class__.__name__}`") from None
        
        if not hasattr(iterable, "gi_running"):
            true_iterable = iterable
        else:
            true_iterable = tuple(iterable)
        
        return self.__class__(
            {k: v for k, v in self.items() if k not in true_iterable}
        )
    
    def __and__(self, other, *args, **kwargs):
        try:
            (little, big) = (
                (self, other) 
                if len(self) < len(other) 
                else (other, self)
            )
            
            try:
                other.items
                res = {k: other[k] for k in little if k in big}
            except Exception:
                res = {k: self[k] for k in little if k in big}
        except Exception:
            raise TypeError(f"Unsupported operand type(s) for &: `{self.__class__.__name__}` and `{other.__class__.__name__}`") from None
        
        return self.__class__(res)


frozendict.clear = notimplemented
frozendict.pop = notimplemented
frozendict.popitem = notimplemented
frozendict.setdefault = notimplemented
frozendict.update = notimplemented
frozendict.__delitem__ = notimplemented
frozendict.__setitem__ = notimplemented
frozendict.__delattr__ = notimplemented
frozendict.__setattr__ = notimplemented
frozendict.empty = frozendict()

__all__ = (frozendict.__name__, )
