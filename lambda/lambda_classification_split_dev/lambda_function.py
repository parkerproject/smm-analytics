import dataset
import plot
from lambda_classification_split import Classification


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """
    output = {}

    CF = Classification(df, params['column'])

    output['uid'] = params['uid']

    training_set, testing_set = CF.split(int(params['ratio']))
    output['training'] = training_set
    output['testing'] = testing_set

    # plot
    labels = ['training set data points', 'unlabeled data points']
    values = [len(training_set), len(testing_set)]
    output['div'] = plot.plot_pie_chart(labels, values,
                                        title='breakdown of training vs testing size')

    return output


def lambda_handler(params, context):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''
    urls = {}

    # arranging the paths
    path = dataset.organize_path_lambda(params)

    # save the config file
    urls['config'] = dataset.save_remote_output(path['localSavePath'],
                                                path['remoteSavePath'],
                                                'config',
                                                params)
    # prepare input dataset
    df = dataset.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    # execute the algorithm
    output = algorithm(df, params)

    # upload object to s3 bucket and return the url
    for key, value in output.items():
        if key != 'uid':
            urls[key] = dataset.save_remote_output(path['localSavePath'],
                                               path['remoteSavePath'],
                                               key,
                                               value)
        else:
            urls[key] = value

    return urls
