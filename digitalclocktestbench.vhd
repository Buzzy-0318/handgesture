LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
-- VHDL project: VHDL code for digital clock
ENTITY tb_digital_clock IS
END tb_digital_clock;


ARCHITECTURE behavior OF tb_digital_clock IS 
  -- Component Declaration for the Unit Under Test (UUT)
    COMPONENT digital_clock
    PORT(
         clk : IN  std_logic;
         rst_n : IN  std_logic;
         H_in1 : IN  std_logic_vector(1 downto 0);
         H_in0 : IN  std_logic_vector(3 downto 0);
         M_in1 : IN  std_logic_vector(3 downto 0);
         M_in0 : IN  std_logic_vector(3 downto 0);
         H_out1 : OUT  std_logic_vector(6 downto 0);
         H_out0 : OUT  std_logic_vector(6 downto 0);
         M_out1 : OUT  std_logic_vector(6 downto 0);
         M_out0 : OUT  std_logic_vector(6 downto 0);
         S_out1 : OUT  std_logic_vector(6 downto 0);
         S_out0 : OUT  std_logic_vector(6 downto 0)
        );
    END COMPONENT;
   --Inputs
   signal clk : std_logic := '0';
   signal rst_n : std_logic := '0';
   signal H_in1 : std_logic_vector(1 downto 0) := (others => '0');
   signal H_in0 : std_logic_vector(3 downto 0) := (others => '0');
   signal M_in1 : std_logic_vector(3 downto 0) := (others => '0');
   signal M_in0 : std_logic_vector(3 downto 0) := (others => '0');

  --Outputs
   signal H_out1 : std_logic_vector(6 downto 0);
   signal H_out0 : std_logic_vector(6 downto 0);
   signal M_out1 : std_logic_vector(6 downto 0);
   signal M_out0 : std_logic_vector(6 downto 0);
   signal S_out1 : std_logic_vector(6 downto 0);
   signal S_out0 : std_logic_vector(6 downto 0);
   
   -- Clock period definitions
   constant clk_period : time := 10 ps;
BEGIN
-- fpga4student.com FPGA projects, VHDL projects, Verilog projects
 -- Instantiate the Unit Under Test (UUT)
   uut: digital_clock PORT MAP (
          clk => clk,
          rst_n => rst_n,
          H_in1 => H_in1,
          H_in0 => H_in0,
          M_in1 => M_in1,
          M_in0 => M_in0,
          H_out1 => H_out1,
          H_out0 => H_out0,
          M_out1 => M_out1,
          M_out0 => M_out0,
          S_out1 => S_out1,
          S_out0 => S_out0
        );
   -- Clock process definitions
   clk_process :process
   begin
        clk <= '0';
        wait for clk_period/2;
        clk <= '1';
        wait for clk_period/2;
   end process;
   
   -- Stimulus process
   stim_proc: process
   begin 
      -- hold reset state for 100 ns.
      rst_n <= '0';
      H_in1 <= "01";  -- Set hour to 10
      H_in0 <= x"0";
      M_in1 <= x"2";  -- Set minute to 20
      M_in0 <= x"0";
      wait for 100 ns; 
      
      -- Release reset and let the clock run
      rst_n <= '1';
      
      -- Let the clock run for a while to observe seconds counting
      wait for clk_period*1000;
      
      -- Test rollover from 59 seconds to 00
      wait until S_out1 = "0010010" and S_out0 = "1000000"; -- Wait for 59 seconds
      wait for clk_period*10; -- Observe minute increment
      
      -- Test rollover from 59 minutes to 00
      -- You might need to adjust the wait time depending on your simulation needs
      wait until M_out1 = "0010010" and M_out0 = "1000000"; -- Wait for 59 minutes
      wait for clk_period*10; -- Observe hour increment
      
      -- Test rollover from 23 hours to 00
      -- You might need to adjust the wait time depending on your simulation needs
      wait until H_out1 = "0110000" and H_out0 = "0010000"; -- Wait for 23 hours
      wait for clk_period*10; -- Observe day rollover
      
      wait;
   end process;

END;
