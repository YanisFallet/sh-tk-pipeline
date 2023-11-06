import pools
import update_traj


update_traj.create_all_tables()

pool_sccrapper = pools.UpdatePools()
pool_sccrapper.run()



update_traj.update_traj_tiktok_to_tiktok()