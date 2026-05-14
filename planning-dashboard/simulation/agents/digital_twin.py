import multiprocessing as mp
import time
import random

def retailer_agent(retailer_id, demand_queue, order_queue, log_queue, simulation_steps):
    """
    Retailer Agent: 
    - Observes market demand from demand_queue
    - Places orders to distributor via order_queue (amplified by bullwhip)
    - Logs actions
    """
    inventory = 100
    for step in range(simulation_steps):
        # 1. Observe Demand
        actual_demand = random.randint(10, 30) # Simulated market demand
        
        # 2. Fulfill Demand
        fulfilled = min(inventory, actual_demand)
        inventory -= fulfilled
        stockout = actual_demand - fulfilled
        
        # 3. Calculate Replenishment Order (s, S policy or similar)
        # Inducing Bullwhip: Order variance is greater than demand variance
        target_inventory = 120
        order_quantity = max(0, target_inventory - inventory + (stockout * 1.5)) 
        
        # 4. Place Order
        order_queue.put({"retailer_id": retailer_id, "step": step, "qty": order_quantity})
        
        # 5. Receive shipment (simplified, assume immediate or next-step delivery from a delivery_queue in full sim)
        # For this prototype, we'll assume they just get a flat amount back for simplicity, or we skip it
        inventory += order_quantity * 0.9 # 90% fill rate assumption for demo
        
        log_queue.put(f"Step {step} | Retailer {retailer_id}: Demand={actual_demand}, Inventory={inventory:.1f}, Ordered={order_quantity:.1f}")
        time.sleep(0.01) # Simulate processing time

def distributor_agent(distributor_id, order_queue, log_queue, simulation_steps, num_retailers):
    """
    Distributor Agent:
    - Receives orders from multiple retailers
    - Aggregates demand
    - Places bulk orders to manufacturer
    """
    inventory = 500
    for step in range(simulation_steps):
        total_orders_received = 0
        orders_processed = 0
        
        # Wait for all retailers to place orders for this step
        # Note: In a robust simulation, synchronization mechanisms (Barriers/Events) are better,
        # but queues work for this prototype.
        while orders_processed < num_retailers:
            try:
                order = order_queue.get(timeout=1.0)
                if order["step"] == step:
                    total_orders_received += order["qty"]
                    orders_processed += 1
                else:
                    # Put it back if it's for a future step (simplification)
                    order_queue.put(order)
            except mp.queues.Empty:
                break # Timeout
                
        # Fulfill to retailers
        fulfilled = min(inventory, total_orders_received)
        inventory -= fulfilled
        
        # Place order to manufacturer
        target_inventory = 600
        order_to_mfg = max(0, target_inventory - inventory)
        inventory += order_to_mfg * 0.8 # 80% manufacturer fill rate
        
        log_queue.put(f"Step {step} | Distributor {distributor_id}: Received Orders={total_orders_received:.1f}, Inventory={inventory:.1f}, Ordered to Mfg={order_to_mfg:.1f}")
        time.sleep(0.01)

def run_digital_twin_simulation(num_retailers=3, steps=10):
    """
    Orchestrates the multi-echelon agent-based simulation using multiprocessing.
    """
    order_queue = mp.Queue()
    log_queue = mp.Queue()
    
    processes = []
    
    # Start Distributor
    distributor = mp.Process(target=distributor_agent, args=("DIST-1", order_queue, log_queue, steps, num_retailers))
    processes.append(distributor)
    distributor.start()
    
    # Start Retailers
    for i in range(num_retailers):
        p = mp.Process(target=retailer_agent, args=(f"RET-{i+1}", None, order_queue, log_queue, steps))
        processes.append(p)
        p.start()
        
    # Wait for completion
    for p in processes:
        p.join()
        
    # Collect logs
    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())
        
    return sorted(logs)

if __name__ == '__main__':
    print("Starting Digital Twin Agent Simulation...")
    results = run_digital_twin_simulation(num_retailers=2, steps=5)
    for r in results:
        print(r)
