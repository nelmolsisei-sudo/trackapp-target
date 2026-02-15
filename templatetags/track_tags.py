from django import template

register = template.Library()

@register.filter(name='clean_last_name')
def clean_last_name(value, request):

    if value and not request.user.is_authenticated:
        return value[0]
    
    return value
        
@register.filter(name='clean_full_name')
def clean_full_name(user, request):

    if user.last_name and not request.user.is_authenticated:
        return f"{user.first_name} {user.last_name[0]}"
    
    return user.get_full_name()
        