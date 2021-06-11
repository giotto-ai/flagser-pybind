from ._version import __version__

__all__ = ['__version__']

# Allows to have access to the version information without
# installating package + dependencies
try:
    from .flagio import load_unweighted_flag, load_weighted_flag, \
        save_unweighted_flag, save_weighted_flag
    from .flagser import flagser_unweighted, flagser_weighted
    from .flagser_count import flagser_count_unweighted, \
        flagser_count_weighted

    __all__ += ['load_unweighted_flag',
                'load_weighted_flag',
                'save_unweighted_flag',
                'save_weighted_flag',
                'flagser_unweighted',
                'flagser_weighted',
                'flagser_count_unweighted',
                'flagser_count_weighted'
                ]
except Exception:
    pass
