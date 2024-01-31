from utils.storageUtils import readSettings


def upload(profile: str, paths: list) -> int:
    vault = readSettings(profile, "vault")
    print(f"Uploading {paths} to {vault}...")

    # TODO: Implement upload logic
    print("Not implemented yet.")
    return -1
