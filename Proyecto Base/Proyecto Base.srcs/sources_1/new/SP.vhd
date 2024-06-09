library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SP is
    Port ( clock    : in  std_logic;                        -- Senal del clock (reducido).
           inc : in std_logic;                           -- Senal de incremento de SP.
           dec : in std_logic;                           -- Senal de decremento de SP.
           clear : in std_logic;                           -- Senal de reset     
           dataout  : out std_logic_vector (11 downto 0));   -- Senales de salida de datos.
end SP;

architecture Behavioral of SP is

component Reg12 is
        Port ( clock    : in  std_logic;                        -- Senal del clock (reducido).
           clear    : in  std_logic;                        -- Senal de reset.
           load     : in  std_logic;                        -- Senal de carga.
           up       : in  std_logic;                        -- Senal de subida.
           down     : in  std_logic;                        -- Senal de bajada.
           datain   : in  std_logic_vector (11 downto 0);   -- Senales de entrada de datos.
           dataout  : out std_logic_vector (11 downto 0));  -- Senales de salida de datos.
end component;

signal sp_datain : std_logic_vector(11 downto 0);

begin

-- penultima direccion de memoria en la que se guarda el SP

inst_Reg: Reg12 port map(
        clock    =>  clock,  
        clear    =>  '0',
        load     =>  clear, -- tiene que ser siempre 1????
        up => inc, -- se puede?
        down => dec, -- se puede?
        datain   =>  "111111111111", --!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        dataout  =>  dataout
);

end Behavioral;
