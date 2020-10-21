def format_playlists(playlists):
    """
    Maps over the given list of playlists to format each to only contain the relevant keys.
    """

    relevant_keys = {'name', 'tracks'}
    return [extract_relevant_keys(pl, relevant_keys) for pl in playlists]


def extract_relevant_keys(target_dict, relevant_keys):
    """
    Extracts the relevant key-value pairs from the given dict. The relevant keys are passed in as
    a tuple of strings.
    """

    return {key: target_dict[key] for key in target_dict.keys() & relevant_keys}
