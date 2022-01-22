def search_values_args_validation(vehicle, driver, between):
    """DBManager.seach_values() arguments validation."""

    if not isinstance(vehicle, str):
        raise TypeError(f"'vehicle' argument must be str not {type(vehicle).__name__} type.")

    if not isinstance(driver, str):
        raise TypeError(f"'vehicle' argument must be str not {type(driver).__name__} type.")

    if not isinstance(between, list) and between is not None:
        raise TypeError(f"'between' argument must be list not {type(between).__name__} type."
                        f" Required date format ['yyyy-mm-dd', 'yyyy-mm-dd'].")
    if isinstance(between, list):
        if len(between) != 2:
            raise Exception("Required date format ['yyyy-mm-dd', 'yyyy-mm-dd'].")
        else:
            for arg in between:
                if not isinstance(arg, str) and arg is not None:
                    raise TypeError("Required date format ['yyyy-mm-dd', 'yyyy-mm-dd'].")
