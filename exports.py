@classmethod
def make_empty(cls, is_simulated: bool = False, num_phases: int = 1) -> PowderExperiment:
    phases = []
    for j in range(num_phases):
        lengths = (float('nan'), float('nan'), float('nan'))
        angles = (float('nan'), float('nan'), float('nan'))
        base = CrystalBasis.empty()

        p = CrystalStructure(lengths=lengths, angles=angles, basis=base)
        phases.append(p)

    xray_info = XrayInfo.mk_empty()
    return cls(phases=phases, crystallite_size=None, temp_in_celcius=None, xray_info=xray_info,
               is_simulated=is_simulated)


def get_list_repr(self) -> list:
    list_repr = []
    structure = self.phases[0]

    a, b, c = structure.lengths
    alpha, beta, gamma = structure.angles
    lattice_params = [a, b, c, alpha, beta, gamma]
    list_repr += lattice_params

    base = structure.basis
    padded_base = self.get_padded_base(base=base, nan_padding=base.is_empty())
    for atomic_site in padded_base:
        list_repr += atomic_site.as_list()

    if structure.spacegroup is None:
        spg_logits_list = [float('nan') for _ in range(NUM_SPACEGROUPS)]
    else:
        spg_logits_list = [1000 if j + 1 == structure.spacegroup else 0 for j in range(NUM_SPACEGROUPS)]
    list_repr += spg_logits_list

    list_repr += self.xray_info.as_list()
    list_repr += [self.is_simulated]

    return list_repr

@staticmethod
def get_padded_base(base: CrystalBasis, nan_padding : bool) -> CrystalBasis:
    def make_padding_site():
        if nan_padding:
            site = AtomSite.make_placeholder()
        else:
            site = AtomSite.make_void()
        return site

    delta = MAX_ATOMIC_SITES - len(base)
    if delta < 0:
        raise ValueError(f'Base is too large! Size = {len(base)} exceeds MAX_ATOMIC_SITES = {MAX_ATOMIC_SITES}')

    padded_base = base + [make_padding_site() for _ in range(delta)]
    return padded_base