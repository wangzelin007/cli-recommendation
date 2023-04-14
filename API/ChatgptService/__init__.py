import logging
import os
import openai
import json
import azure.functions as func

from .src.util import get_param_str, get_param_list

# initialize_openai_service
# the type of the OpenAI API service
openai.api_type = "azure"
# the key of the OpenAI API service
openai.api_key = os.environ["OPENAI_API_KEY"]
# the version of the OpenAI API service
openai.api_version = os.environ["OPENAI_API_VERSION"]
# the url of the OpenAI API service
openai.api_base = os.environ["OPENAI_API_URL"]


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Chatgpt Service HTTP trigger function processed a request.')
    response_data = {"content": None, "history_msg_list": None}
    # the param dict of the chatgpt service
    user_msg = get_param_str(req, "user_msg", required=True)
    history_msg_list = get_param_list(req, "history_msg")
    chatgpt_service_params = initialize_chatgpt_service_params()
    if history_msg_list:
        chatgpt_service_params["messages"].extend(history_msg_list)
    chatgpt_service_params["messages"].append(
        {"role": "user", "content": user_msg})
    try:
        response = openai.ChatCompletion.create(**chatgpt_service_params)
        content = response["choices"][0]["message"]["content"]
        history_msg_list.append({"role": "user", "content": user_msg})
        history_msg_list.append({"role": "assistant", "content": content})
        response_data["content"] = content
        response_data["history_msg"] = history_msg_list
        return func.HttpResponse(generate_response(data=response_data, status=200))
    except:
        return func.HttpResponse('There is some error from the server.', status_code=400)


def initialize_chatgpt_service_params():
    # use a dict to store the parameters of the chatgpt service
    # give initial values to the parameters
    default_msg = [{"role": "system", "content": "You are an assistant who guide others to use Azure CLI and only provide advice on Azure CLI commands or command combinations. \nYou can complete the task in three steps:\n1. Parse the task that the user wants to accomplish\n2. Determine how many commands are needed to complete the task\n3. If only one command is needed, please output an example of that command. If multiple commands are required, please output an example of a set of commands\nAll output must be in the format shown in the follow few-shot examples, Each output must contain a 'Description' property to briefly describe the function of the Script, a 'CommandSet' property containing examples and descriptions of all the commands, and a 'Reason' property detailing the function and flow of the script."}, {"role": "user", "content": "How to Create an Azure Function that connects to an Azure Storage"}, {"role": "assistant", "content": "{'Description': 'Create an Azure Function that connects to an Azure Storage', 'CommandSet': [{'command': 'storage account create', 'arguments': ['--name', '--location', '--resource-group', '--sku'], 'reason': 'Create an Azure storage account in the resource group.', 'example': 'az storage account create --name $storage --location $location --resource-group $resourceGroup --sku $skuStorage'}, {'command': 'functionapp create', 'arguments': ['--name', '--resource-group', '--storage-account', '--consumption-plan-location', '--functions-version'], 'reason': 'Create a serverless function app in the resource group.', 'example': 'az functionapp create --name $functionApp --resource-group $resourceGroup --storage-account $storage --consumption-plan-location $location --functions-version $functionsVersion'}, {'command': 'storage account show-connection-string', 'arguments': ['--name', '--resource-group', '--query', '--output'], 'reason': 'Get the storage account connection string. (connstr will be used in subsequent commands).', 'example': 'az storage account show-connection-string --name $storage --resource-group $resourceGroup --query connectionString --output tsv'}, {'command': 'functionapp config appsettings set', 'arguments': ['--name', '--resource-group', '--settings'], 'reason': 'Update function app settings to connect to the storage account.', 'example': 'az functionapp config appsettings set --name $functionApp --resource-group $resourceGroup --settings StorageConStr=$connstr'}], 'Reason': 'Create an Azure Function that connects to an Azure Storage'}"}, {"role": "user", "content": "Please help me create a resource group"}, {"role": "assistant", "content": "{'Description': 'Create a Resource Group', 'CommandSet': [{'command': 'resource group create', 'arguments': ['--name', '--location'], 'reason': 'Create a resource group', 'example': 'az group create --name $resourceGroup  --location $location'}], 'Reason': 'Create a Resource Group by defining group name and location'}"}, {"role": "user", "content": "I want to create a website with service and database"}, {"role": "assistant", "content": "{'Description': 'Connect an app to MongoDB (Cosmos DB).', 'CommandSet': [{'command': 'appservice plan create', 'arguments': ['--name', '--resource-group', '--location'], 'reason': 'Create an App Service Plan', 'example': 'az appservice plan create --name $appServicePlan --resource-group $resourceGroup --location $location'}, {'command': 'webapp create', 'arguments': ['--name', '--plan', '--resource-group'], 'reason': 'Create a Web App', 'example': 'az webapp create --name $webapp --plan $appServicePlan --resource-group $resourceGroup'}, {'command': 'cosmosdb create', 'arguments': ['--name', '--resource-group', '--kind'], 'reason': 'Create a Cosmos DB with MongoDB API', 'example': 'az cosmosdb create --name $cosmosdb --resource-group $resourceGroup --kind MongoDB'}, {'command': 'cosmosdb keys list', 'arguments': ['--name', '--resource-group', '--type', '--query', '--output'], 'reason': 'Get the MongoDB URL (connectionString will be used in subsequent commands).', 'example': 'az cosmosdb keys list --name $cosmosdb --resource-group $resourceGroup --type connection-strings --query connectionStrings[0].connectionString --output tsv'}, {'command': 'webapp config appsettings set', 'arguments': ['--name', '--resource-group', '--settings'], 'reason': 'Assign the connection string to an App Setting in the Web App', 'example': 'az webapp config appsettings set --name $webapp --resource-group $resourceGroup --settings MONGODB_URL=$connectionString'}], 'Reason': 'Connect an app to MongoDB (Cosmos DB).'}"}, {
        "role": "user", "content": "Could you please help me create a resource group named bocheng-test and create a webapp 'test-webapp' with cosmosdb 'test-cosmosdb' under the resource group and at last upload the web code from local folder?"}, {"role": "assistant", "content": "{'Description': 'Create a resource group, webapp, Cosmos DB, and upload web code', 'CommandSet': [{'command': 'group create', 'arguments': ['--name', '--location'], 'reason': 'Create a resource group named bocheng-test', 'example': 'az group create --name bocheng-test --location $location'}, {'command': 'appservice plan create', 'arguments': ['--name', '--resource-group', '--location'], 'reason': 'Create an App Service Plan', 'example': 'az appservice plan create --name $appServicePlan --resource-group bocheng-test --location $location'}, {'command': 'webapp create', 'arguments': ['--name', '--plan', '--resource-group'], 'reason': 'Create a Web App named test-webapp', 'example': 'az webapp create --name test-webapp --plan $appServicePlan --resource-group bocheng-test'}, {'command': 'cosmosdb create', 'arguments': ['--name', '--resource-group', '--kind'], 'reason': 'Create a Cosmos DB named test-cosmosdb', 'example': 'az cosmosdb create --name test-cosmosdb --resource-group bocheng-test --kind MongoDB'}, {'command': 'cosmosdb keys list', 'arguments': ['--name', '--resource-group', '--type', '--query', '--output'], 'reason': 'Get the MongoDB URL (connectionString will be used in subsequent commands).', 'example': 'az cosmosdb keys list --name test-cosmosdb --resource-group bocheng-test --type connection-strings --query connectionStrings[0].connectionString --output tsv'}, {'command': 'webapp config appsettings set', 'arguments': ['--name', '--resource-group', '--settings'], 'reason': 'Assign the connection string to an App Setting in the Web App', 'example': 'az webapp config appsettings set --name test-webapp --resource-group bocheng-test --settings MONGODB_URL=$connectionString'}, {'command': 'webapp deployment source config-zip', 'arguments': ['--name', '--resource-group', '--src'], 'reason': 'Deploy the web code from local folder', 'example': 'az webapp deployment source config-zip --name test-webapp --resource-group bocheng-test --src $localFolderPath'}], 'Reason': 'Create a resource group, webapp, Cosmos DB, and upload web code'}"}, {"role": "user", "content": "Use Azure Data Lake Storage Gen2 with Azure HDInsight clusters using Azure CLI."}, {"role": "assistant", "content": "{'Description': 'Use Azure Data Lake Storage Gen2 with Azure HDInsight clusters using Azure CLI', 'CommandSet': [{'command': 'storage account create', 'arguments': ['--name', '--location', '--resource-group', '--sku', '--kind', '--hierarchical-namespace'], 'reason': 'Create a Data Lake Storage Gen2 account', 'example': 'az storage account create --name $storageAccount --location $location --resource-group $resourceGroup --sku Standard_LRS --kind StorageV2 --hierarchical-namespace true'}, {'command': 'storage account keys list', 'arguments': ['--account-name', '--resource-group', '--query', '--output'], 'reason': 'Get the storage account key (storageAccountKey will be used in subsequent commands).', 'example': 'az storage account keys list --account-name $storageAccount --resource-group $resourceGroup --query [0].value --output tsv'}, {'command': 'hdinsight create', 'arguments': ['--name', '--resource-group', '--type', '--component-version', '--storage-account', '--storage-account-key', '--location', '--cluster-tier'], 'reason': 'Create an HDInsight cluster with Data Lake Storage Gen2', 'example': 'az hdinsight create --name $hdinsightCluster --resource-group $resourceGroup --type $clusterType --component-version $componentVersion --storage-account $storageAccount --storage-account-key $storageAccountKey --location $location --cluster-tier $clusterTier'}], 'Reason': 'Create a Data Lake Storage Gen2 account and configure it with an Azure HDInsight cluster using Azure CLI'}"}]
    chatgpt_service_params = {"engine": "GPT_4_32k", "temperature": 0.5, "max_tokens": 800,
                              "top_p": 0.95, "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    for key, value in chatgpt_service_params.items():
        chatgpt_service_params[key] = os.environ.get(key, default=value)
        if key in ["temperature", "top_p"]:
            chatgpt_service_params[key] = float(chatgpt_service_params[key])
        elif key in ["max_tokens", "frequency_penalty", "presence_penalty"]:
            chatgpt_service_params[key] = int(chatgpt_service_params[key])
    default_msg = json.loads(os.environ.get(
        "OPENAI_DEFAULT_MSG", default=default_msg))
    chatgpt_service_params["messages"] = default_msg
    return chatgpt_service_params


def generate_response(data, status, error=None):
    response_data = {
        'data': data,
        'error': error,
        'status': status,
        # The version of the API, which is defined in the function app settings and can be changed without redeploying the whole function.
        'api_version': os.environ["API_Version"]
    }
    return json.dumps(response_data)
