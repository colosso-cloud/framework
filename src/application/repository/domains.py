modules = {'factory': 'framework.service.factory',}

repository = factory.repository(
    location = {'SUPABASE': ['domains']},
    model = 'domain',
    mapper = {},
)