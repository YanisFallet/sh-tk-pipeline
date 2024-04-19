import pools
import update_traj
from logging_config import logger



def main():
    # create all tables if not exist
    update_traj.create_all_tables()


    # run the pool scrapper
    # pool_sccrapper = pools.UpdatePools()
    # pool_sccrapper.run()

    # update the trajectories
    update_traj.update_traj_instagram_to_tiktok()
    
    logger.info(f"{__name__} : Finished")
    print("Finished")
    
if __name__ == "__main__":
    main()

