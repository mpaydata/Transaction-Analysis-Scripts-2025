# Define function to calculate bank partner's charge
def partner_charge(amount):
    M_charge = 0.013 * amount  # 1.3%
    return min(M_charge, 2000)  # Apply ₦2000 cap

