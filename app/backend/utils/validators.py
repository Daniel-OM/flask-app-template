import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email):
    """
    Validar formato de correo electrónico.
    
    Args:
        email (str): El correo electrónico a validar
        
    Returns:
        bool: True si el email es válido, False si no lo es
    """
    try:
        # Validar email usando email_validator
        valid = validate_email_lib(email)
        return True
    except EmailNotValidError:
        return False


def validate_password(password):
    """
    Validar que la contraseña cumpla con los requisitos mínimos:
    - Al menos 8 caracteres
    - Al menos una letra
    - Al menos un número
    
    Args:
        password (str): La contraseña a validar
        
    Returns:
        bool: True si la contraseña es válida, False si no lo es
    """
    if not password or len(password) < 8:
        return False
    
    # Verificar que tiene al menos una letra
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    # Verificar que tiene al menos un número
    if not re.search(r'\d', password):
        return False
    
    return True


def validate_phone(phone):
    """
    Validar formato de número de teléfono (formato español)
    
    Args:
        phone (str): El número de teléfono a validar
        
    Returns:
        bool: True si el teléfono es válido, False si no lo es
    """
    # Eliminar espacios y guiones
    clean_phone = re.sub(r'[\s-]', '', phone)
    
    # Verificar si es un número español válido
    # Patrones para:
    # - Móviles: 6XXXXXXXX o 7XXXXXXXX
    # - Fijos: 9XXXXXXXX o 8XXXXXXXX
    pattern = r'^(6|7|8|9)\d{8}$'
    
    return bool(re.match(pattern, clean_phone))


def validate_postal_code(postal_code, country='ES'):
    """
    Validar formato de código postal según el país
    
    Args:
        postal_code (str): El código postal a validar
        country (str): Código ISO del país (por defecto ES para España)
        
    Returns:
        bool: True si el código postal es válido, False si no lo es
    """
    if country == 'ES':
        # Código postal español: 5 dígitos
        return bool(re.match(r'^\d{5}$', postal_code))
    
    # Por defecto, validación general (1-10 caracteres alfanuméricos)
    return bool(re.match(r'^[a-zA-Z0-9]{1,10}$', postal_code))