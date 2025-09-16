from langchain_aws import ChatBedrock, ChatBedrockConverse

model_sonnet_37 = ChatBedrockConverse(
        model='us.anthropic.claude-sonnet-4-20250514-v1:0',
        region_name='us-west-2',
        credentials_profile_name='hackaton'

        # aws_access_key_id=_model_settings.access_key_id,
        # aws_secret_access_key=_model_settings.secret_access_key,
        # thinking_params=thinking_params,
    )

if __name__ == '__main__':
    print(model_sonnet_37.invoke('Hola jefe'))