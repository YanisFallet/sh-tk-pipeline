import os
import json

class ArcManagement: 
    def __init__(self, src_p : str = None, dist_p : str = None): 
        self.src_p = src_p
        self.dist_p = dist_p
    
    def traj_connection(func):
        def wrapper(self, *args, **kwargs):
            file_path = os.path.join(f"arc/traj", f"{self.src_p}->{self.dist_p}.json")
            try:
                with open(file_path, "r") as f:
                    arc = json.load(f)
            except FileNotFoundError:
                arc = None
            if arc is not None:
                return func(self, arc, *args, **kwargs)
        return wrapper
            
    def dist_connection(func): 
        def wrapper(self, *args, **kwargs):
            file_path = os.path.join(f"arc/dist", f"{self.dist_p}.json")
            try:
                with open(file_path, "r") as f:
                    arc = json.load(f)
            except FileNotFoundError:
                arc = None
            return func(self, arc, *args, **kwargs)
        return wrapper
    
    @traj_connection
    def get_src(self, arc, return_pools = False):
        src = []
        pools = []
        if self.dist_p in ["youtube", 'tiktok']:
            for account in arc.keys():
                for pool in arc[account].keys():
                    c = arc[account][pool].get("src", [])
                    if len(c) > 0:
                        src.extend(c)
                        pools.append(pool)
        else :
            for pool in arc.keys():
                c = arc[pool].get("src", [])
                if len(c) > 0:
                    src.extend(c)
                    pools.append(pool)
                    
        if return_pools:
            return src, pools
        else:
            return src
    
    @traj_connection
    def get_dist(self, arc):
        dist = []
        if self.dist_p in ["youtube", 'tiktok']:
            for account in arc.keys():
                for pool in arc[account].values():
                    dist.extend(pool.get("dist", []))
        else :
            for pool in arc.values():
                dist.extend(pool.get("dist", []))
        return dist
    
    @traj_connection
    def get_dist_by_google_account(self, arc, google_account_name : str):
        self.google_account_is_valid(google_account_name)
        dist = []
        for account in arc.keys():
            if account == google_account_name:
                for pool in arc[account].values():
                    dist.extend(pool.get("dist", []))
                return dist
        return []
            
            
    @traj_connection
    def get_dist_by_pool(self, arc, pool):
        if self.dist_p == "youtube":
            for account in arc.keys():
                if pool in arc[account].keys():
                    return arc[account][pool].get("dist", [])
        else :
            if pool in arc.keys():
                return arc[pool].get("dist", [])
        return []
    
    def get_pools_by_platform(self): 
        file_path = os.path.join(f"arc/pools", f"{self.src_p}.json")
        try:
            with open(file_path, "r") as f:
                arc = json.load(f)
        except FileNotFoundError:
            arc = None
            return [], []
        pools = []
        type_pools = []
        for type_pool in arc.keys():
            pools.extend(arc[type_pool])
            type_pools.extend([type_pool] * len(arc[type_pool]))
        return pools, type_pools
            
                    
    def google_account_is_valid(self, google_account_name : str):
        with open(os.path.join("arc/utils/google_dir.json"), "r") as f:
            google_dir = json.load(f)
        if not google_account_name in google_dir.keys():
            raise Exception(f"Google account '{google_account_name}' not found")
    
    def get_google_accounts(self):
        with open(os.path.join("arc/utils/google_dir.json"), "r") as f:
            return  json.load(f).keys()