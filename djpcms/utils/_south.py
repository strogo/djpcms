
from south.modelsinspector import add_introspection_rules
from fields import SlugCode

rules = [
         (
          (SlugCode, ),
          [],
          {
           "rtxchar": ["rtxchar", {"default": '-'}],
           "lower": ["lower", {"default": False}],
           "upper": ["upper", {"default": False}],
          },
         ),
        ]


add_introspection_rules(rules, ["^djpcms\.djutils\.fields",])
