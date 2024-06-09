library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity PC is
    Port ( clock    : in  std_logic;                        -- Se?al del clock (reducido).
           clear    : in  std_logic;                        -- Se?al de reset.
           loadPC : in std_logic;
           datain : in std_logic_vector (11 downto 0);
           dataout  : out std_logic_vector (11 downto 0));   -- Se?ales de salida de datos.
end PC;

architecture Behavioral of PC is

--component Adder12
  --  Port ( a  : in  std_logic_vector (11 downto 0);
    --       b  : in  std_logic_vector (11 downto 0);
    --       ci : in  std_logic;
    --       s  : out std_logic_vector (11 downto 0);
    --       co : out std_logic);

--end component ;

component Reg12 is
        Port ( clock    : in  std_logic;                        -- Se?al del clock (reducido).
           clear    : in  std_logic;                        -- Se?al de reset.
           load     : in  std_logic;                        -- Se?al de carga.
           up       : in  std_logic;                        -- Se?al de subida.
           down     : in  std_logic;                        -- Se?al de bajada.
           datain   : in  std_logic_vector (11 downto 0);   -- Se?ales de entrada de datos.
           dataout  : out std_logic_vector (11 downto 0));  -- Se?ales de salida de datos.
end component;


signal pc_datain : std_logic_vector(11 downto 0);
signal reg_out : std_logic_vector(11 downto 0); -- Senales de salida del registro. Parte en 0.
signal reg_in : std_logic_vector (11 downto 0);


begin
        
dataout <= reg_out;
pc_datain <= datain;
    
inst_Reg: Reg12 port map(
        clock    =>  clock,  
        clear    =>  clear,
        load     =>  loadPC,
        up => '1',
        down => '0',
        datain   =>   reg_in ,  
        dataout  =>  reg_out
);
    
with loadPC select
     reg_in <= pc_datain when '1',
               reg_out  when others;
             
end Behavioral;