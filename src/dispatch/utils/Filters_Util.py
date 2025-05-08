
from typing import Optional, List, Dict, Any, Tuple  
from sqlalchemy import and_  


from typing import Optional, List, Dict, Any, Tuple, TypeVar  
from sqlalchemy.ext.declarative import as_declarative, declared_attr  
  
# 使用 TypeVar 来定义一个泛型类型，它将代表任何 SQLAlchemy 模型  
Model = TypeVar('Model')  


def get_list_by_param(db_session,  model: Model,filters: List[Dict[str, Tuple[str, Any]]]) -> Optional[List[Model]]:  
    """  
    Returns a list of SemiEndUseManual instances matching the given filter criteria.  
      
    Args:  
        db_session (Session): The database session to use for querying.  
        filters (List[Dict[str, Tuple[str, Any]]]): A list of dictionaries, each containing  
                              a field name, an operator ('eq' for ==, 'ne' for !=, 'is_not_null' for is not null),  
                              and a value to use as filter criteria.  
      
    Returns:  
        Optional[List[SemiEndUseManual]]: The matched instances or an empty list if no matches are found.  
        
        
    such as:
    
    filters = [  
        {'field': 'id', 'operator': 'gt', 'value': 100},  
        {'field': 'price', 'operator': 'lt', 'value': 500},  
        {'field': 'name', 'operator': 'ne', 'value': 'Special Item'},  
        {'field': 'description', 'operator': 'is_not_null', 'value': None},  
    ]  
    """  
    query = db_session.query(model)  
      
    # Build the query dynamically based on the provided filters  
    filter_conds = []  
    for filter_dict in filters:  
        field_name = filter_dict['field']  
        operator, value = filter_dict['operator'], filter_dict['value']  
        model_field = getattr(model, field_name)
        if operator == 'eq':  
            filter_conds.append(model_field== value)  
        elif operator == 'ne':  
            filter_conds.append(model_field != value)  
        elif operator == 'is_not_null':  
            filter_conds.append(model_field.isnot(None))  
        elif operator == 'gt':  
            filter_conds.append(model_field > value)  
        elif operator == 'lt':  
            filter_conds.append(model_field < value)  
        # 可以添加更多的操作符支持，如 'lt' (小于), 'le' (小于等于), 'gt' (大于), 'ge' (大于等于) 等  
      
    if filter_conds:  
        query = query.filter(and_(*filter_conds))  
      
    # Execute the query and return the results  
    return query.all()  
  
