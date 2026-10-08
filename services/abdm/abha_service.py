from integrations.mock_abdm.mock_abha import lookup, create_mock
def get_profile(abha_id): return lookup(abha_id)
def generate_for_demo(identifier): return create_mock(identifier)
