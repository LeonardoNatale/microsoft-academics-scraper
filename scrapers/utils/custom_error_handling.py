from typing import Tuple, Callable, Any


def custom_error_handling(exceptions: Tuple[Exception], default_return_value: Any = None) -> Callable:
    """
    Custom error handling annotation. The purpose of this function is to allow parameters to be used inside the
    annotation.
    When annotated, a function can be called adding a parameter `:param ignore_exceptions` that will determine if
    the exceptions declared in the definition of the annotation should be ignored or not.

    :param exceptions: The exceptions that are to be ignored when ignore_exceptions is true, as a Tuple.
    :param default_return_value: The value to return when exceptions are ignored but the function failed
    anyways. Defaults to None.
    :return: The function it annotates, wrapped in a custom error handling process.
    """
    def custom_error_handler(func: Callable) -> Callable:
        """
        Annotation handler, that returns the error handler function.

        :param func: The function to annotate.
        :return: The annotated function.
        """
        def handle_error(*args, **kwargs):
            """
            Handles errors depending on the value of the parameter `:param ignore_exceptions` of the function called.
            :param args: Arguments of the function.
            :param kwargs: Named arguments of the function.
            :return: The return value of the function if no exception occurs, otherwise, a default return value if the
            value of `:param ignore_exceptions` is True, if returns a default return value defined in the annotation. If
            the value is False, then the exception is raised.
            """
            # Getting the value of the `ignore_exceptions` parameter in the function call. If not provided, will raise
            # by default.
            ignore = kwargs.pop('ignore_exceptions', None)
            try:
                # Tries to execute the function.
                return func(*args, **kwargs)
            except exceptions as e:
                # If an exception occurs, if `ignore` is True, then default value is returned.
                if ignore:
                    return default_return_value
                # Else, the previously caught error is raised again.
                else:
                    raise e
        return handle_error
    return custom_error_handler
