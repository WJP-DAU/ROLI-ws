import importlib

target = "niger_barreauduniger"
stage  = 1

def main(target, stage):

    print("/////////////////////////////////////////////////////////////")
    print(f"Extracting information from: {target}")
    print(f"Stage: {stage}")
    print("/////////////////////////////////////////////////////////////")

    try:
        module = importlib.import_module(f"src.{target}")
        if hasattr(module, "run"):
            module.run(stage) 
        else:
            print(f"Module '{target}' does not define a 'run' function.")
    except ModuleNotFoundError:
        print(f"Module '{target}' not found.")

if __name__ == "__main__":
    main(target, stage)