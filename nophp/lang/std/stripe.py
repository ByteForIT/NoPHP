import stripe
from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *

class CommonStripeMod(Module):
    name="COMMONSTRIPE"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def base(self, tree, ref=False):
        values = []

        if 'FUNCTION_ARGUMENTS' not in tree:
            # Advanced handling
            for var in tree:
                value = self.ref_resolve(var) if ref else self.safely_resolve(var)
                values.append(value)
        else:
            if 'POSITIONAL_ARGS' in tree['FUNCTION_ARGUMENTS']:
                for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:

                    value = self.ref_resolve(var) if ref else self.safely_resolve(var)

                    values.append(value)

        return values


# stripe_set_key($value) -> Bool
class SetSecretMod(CommonStripeMod):
    name="stripe_set_key"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        key = values[0]

        stripe.api_key = key

        return Bool(True)
    
# stripe_intent($amount, $currency) -> String[client_secret]
class StripeIntentMod(CommonStripeMod):
    name="stripe_intent"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        amount, currency = values[0], values[1]
        intent = stripe.PaymentIntent.create(
            amount=amount,  
            currency=currency,
            # Additional options can be passed here (e.g., customer ID)
        )
        print(amount, currency)

        return String(intent.client_secret)
    

# stripe_session($payment_types, $line_items, $success_url, $cancel_url) -> String[id]
class StripeNewSessionMod(CommonStripeMod):
    name="stripe_session"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        payment_types, line_items, success, cancel = values[0], values[1], values[2], values[3]

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=payment_types,
                line_items=line_items,
                # [{
                #     'price_data': {
                #         'currency': 'usd',
                #         'product_data': {
                #             'name': 'T-shirt',
                #         },
                #         'unit_amount': 2000,
                #     },
                #     'quantity': 1,
                # }],
                mode='payment',
                success_url=success,
                cancel_url=cancel,
            )
            return String(session.id)
        except Exception as e:
            return String(f"Failed due to {e}")

    
_MODS = {
    "stripe_set_key": SetSecretMod,
    "stripe_intent": StripeIntentMod,
    "stripe_session": StripeNewSessionMod,
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions